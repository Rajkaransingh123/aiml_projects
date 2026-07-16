import subprocess
import os
from deep_translator import GoogleTranslator
import edge_tts
import asyncio
import whisper
import datetime
import sys

# ---------------- CONFIG ---------------- #
LANGUAGE_MAPPINGS = {
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "gu": "Gujarati",
}

EDGE_TTS_VOICES = {
    "hi": "hi-IN-SwaraNeural",
    "mr": "mr-IN-AarohiNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "bn": "bn-IN-BashkarNeural",
    "gu": "gu-IN-NiranjanNeural",
}

# ---------------- INPUT ---------------- #
if len(sys.argv) < 3:
    print("Usage: python main.py <video_file> <language_code>")
    sys.exit(1)

input_file = sys.argv[1]
target_language = sys.argv[2]

if target_language not in LANGUAGE_MAPPINGS:
    print("Invalid language")
    sys.exit(1)

base_name = os.path.splitext(os.path.basename(input_file))[0]

# ---------------- WHISPER ---------------- #
model = whisper.load_model("base")
result = model.transcribe(input_file)

# ---------------- CREATE SRT ---------------- #
subtitle_file = f"{base_name}.srt"

with open(subtitle_file, "w", encoding="utf-8") as f:
    for i, seg in enumerate(result["segments"]):
        start = str(datetime.timedelta(seconds=seg["start"]))[:12].replace(".", ",")
        end = str(datetime.timedelta(seconds=seg["end"]))[:12].replace(".", ",")

        f.write(f"{i+1}\n{start} --> {end}\n{seg['text']}\n\n")

# ---------------- TRANSLATE ---------------- #
def translate_text(text):
    return GoogleTranslator(source="auto", target=target_language).translate(text)

def translate_srt(file):
    new_file = f"{base_name}_translated.srt"

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if "-->" in line or line.strip().isdigit() or line.strip() == "":
            new_lines.append(line)
        else:
            new_lines.append(translate_text(line.strip()) + "\n")

    with open(new_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    return new_file

# ---------------- PARSE ---------------- #
def parse_srt(file):
    with open(file, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()]

    segments = []
    i = 0
    while i < len(lines):
        if lines[i].isdigit():
            start, end = lines[i+1].split(" --> ")
            text = lines[i+2]
            segments.append((start, end, text))
            i += 4
        else:
            i += 1
    return segments

def time_to_sec(t):
    t = t.replace(",", ".")
    h, m, s = t.split(":")
    return float(h)*3600 + float(m)*60 + float(s)

# ---------------- TTS ---------------- #
async def tts(text, output):
    voice = EDGE_TTS_VOICES[target_language]
    await edge_tts.Communicate(text, voice).save(output)

def generate_tts(text, output):
    asyncio.run(tts(text, output))

# ---------------- PROCESS ---------------- #
translated = translate_srt(subtitle_file)
segments = parse_srt(translated)

audio_files = []
prev_end = 0

for i, (start, end, text) in enumerate(segments):
    start_s = time_to_sec(start)
    end_s = time_to_sec(end)
    duration = end_s - start_s

    if duration <= 0:
        continue

    tts_file = f"tts_{i}.mp3"
    generate_tts(text, tts_file)

    # silence
    if start_s > prev_end:
        silence = f"silence_{i}.mp3"
        subprocess.run([
            "ffmpeg", "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo",
            "-t", str(start_s - prev_end),
            "-y", silence
        ])
        audio_files.append(silence)

    audio_files.append(tts_file)
    prev_end = end_s

# ---------------- MERGE AUDIO ---------------- #
concat = "concat.txt"
with open(concat, "w") as f:
    for file in audio_files:
        f.write(f"file '{file}'\n")

final_audio = f"{base_name}_audio.mp3"

subprocess.run([
    "ffmpeg", "-f", "concat", "-safe", "0",
    "-i", concat, "-c", "copy", "-y", final_audio
])

# ---------------- MERGE VIDEO ---------------- #
output = f"{base_name}_output_video.mp4"

subprocess.run([
    "ffmpeg", "-i", input_file, "-i", final_audio,
    "-map", "0:v", "-map", "1:a",
    "-c:v", "copy", "-shortest", "-y", output
])

print("SUCCESS")