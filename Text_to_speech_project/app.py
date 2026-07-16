# from flask import Flask, request, render_template, jsonify, send_file
# import os
# import subprocess
# import threading
# import time
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'
# app.config['OUTPUT_FOLDER'] = 'outputs'
# app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
# app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}

# # Create directories if they don't exist
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# # Global processing status
# processing_status = {
#     "state": "idle",
#     "progress": 0,
#     "message": "",
#     "current_file": "",
#     "output_file": "",
#     "target_language": ""
# }

# # Language mapping for display names
# LANGUAGE_NAMES = {
#     'hi': 'Hindi',
#     'mr': 'Marathi',
#     'ta': 'Tamil',
#     'gu': 'Gujarati',
#     'bn': 'Bengali',
#     'te': 'Telugu'
# }

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     global processing_status
    
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
        
#     file = request.files['file']
    
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
        
#     if not allowed_file(file.filename):
#         return jsonify({'error': 'Invalid file type'}), 400

#     if processing_status['state'] == 'processing':
#         return jsonify({'error': 'System busy processing another file'}), 429

#     target_language = request.form.get('target_language', 'hi')
    
#     # Validate target language
#     if target_language not in ['hi', 'mr', 'ta', 'gu', 'bn', 'te']:
#         return jsonify({'error': 'Invalid target language'}), 400

#     try:
#         filename = secure_filename(file.filename)
#         upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(upload_path)
        
#         # Get language display name
#         language_name = LANGUAGE_NAMES.get(target_language, target_language)
        
#         # Update processing status
#         processing_status.update({
#             "state": "processing",
#             "progress": 0,
#             "message": f"Initializing processing for {language_name} translation",
#             "current_file": filename,
#             "output_file": "",
#             "target_language": target_language
#         })
        
#         # Start processing thread
#         processing_thread = threading.Thread(
#             target=process_video,
#             args=(upload_path, filename, target_language)
#         )
#         processing_thread.start()
        
#         return jsonify({
#             'message': f'File {filename} uploaded successfully for {language_name} translation',
#             'filename': filename,
#             'target_language': target_language
#         })
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# def process_video(filepath, original_filename, target_language):
#     global processing_status
#     base_name = os.path.splitext(original_filename)[0]
#     language_name = LANGUAGE_NAMES.get(target_language, target_language)
    
#     try:
#         processing_status['message'] = f"Starting video processing for {language_name} translation"
        
#         # Run main.py with the uploaded file and target language
#         result = subprocess.run(
#             ['python', 'main.py', filepath, target_language],
#             capture_output=True,
#             text=True
#         )
        
#         if result.returncode != 0:
#             raise Exception(f"Processing failed: {result.stderr}")
        
#         # Verify output file
#         expected_output = f"{base_name}_output_video.mp4"
#         if not os.path.exists(expected_output):
#             raise Exception("Output file not generated")
            
#         # Move to outputs directory
#         output_filename = f"{base_name}_{language_name}.mp4"
#         output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
#         os.rename(expected_output, output_path)
        
#         # Update final status
#         processing_status.update({
#             "state": "completed",
#             "progress": 100,
#             "message": f"Processing completed successfully. {language_name} translation ready!",
#             "output_file": output_filename
#         })
        
#     except Exception as e:
#         processing_status.update({
#             "state": "error",
#             "message": f"Error: {str(e)}",
#             "output_file": ""
#         })
        
#     finally:
#         # Cleanup upload after processing
#         if os.path.exists(filepath):
#             try:
#                 os.remove(filepath)
#             except:
#                 pass

# @app.route('/status')
# def get_status():
#     return jsonify(processing_status)

# @app.route('/download/<filename>')
# def download_file(filename):
#     safe_filename = secure_filename(filename)
#     file_path = os.path.join(app.config['OUTPUT_FOLDER'], safe_filename)
    
#     if os.path.exists(file_path):
#         return send_file(file_path, as_attachment=True)
#     return jsonify({'error': 'File not found'}), 404

# @app.route('/reset', methods=['POST'])
# def reset_system():
#     global processing_status
#     processing_status = {
#         "state": "idle",
#         "progress": 0,
#         "message": "",
#         "current_file": "",
#         "output_file": "",
#         "target_language": ""
#     }
#     return jsonify({'message': 'System reset successfully'})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, render_template, jsonify, send_file
import os
import subprocess
import threading
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Use absolute paths based on where app.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(BASE_DIR, 'outputs')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Global processing status
processing_status = {
    "state": "idle",
    "progress": 0,
    "message": "",
    "current_file": "",
    "output_file": "",
    "target_language": ""
}

# Language mapping for display names
LANGUAGE_NAMES = {
    'hi': 'Hindi',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'gu': 'Gujarati',
    'bn': 'Bengali',
    'te': 'Telugu'
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global processing_status
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    if processing_status['state'] == 'processing':
        return jsonify({'error': 'System busy processing another file'}), 429

    target_language = request.form.get('target_language', 'hi')
    
    if target_language not in ['hi', 'mr', 'ta', 'gu', 'bn', 'te']:
        return jsonify({'error': 'Invalid target language'}), 400

    try:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        language_name = LANGUAGE_NAMES.get(target_language, target_language)
        
        processing_status.update({
            "state": "processing",
            "progress": 0,
            "message": f"Initializing processing for {language_name} translation",
            "current_file": filename,
            "output_file": "",
            "target_language": target_language
        })
        
        processing_thread = threading.Thread(
            target=process_video,
            args=(upload_path, filename, target_language)
        )
        processing_thread.start()
        
        return jsonify({
            'message': f'File {filename} uploaded successfully for {language_name} translation',
            'filename': filename,
            'target_language': target_language
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_video(filepath, original_filename, target_language):
    global processing_status
    base_name = os.path.splitext(os.path.basename(filepath))[0]  # FIX: use basename of full path
    language_name = LANGUAGE_NAMES.get(target_language, target_language)
    
    try:
        processing_status['message'] = f"Starting video processing for {language_name} translation"
        
        # Run main.py with absolute path to the file
        main_py = os.path.join(BASE_DIR, 'main.py')
        result = subprocess.run(
            ['python', main_py, filepath, target_language],
            capture_output=True,
            text=True,
            cwd=BASE_DIR  # FIX: always run from project folder
        )
        
        if result.returncode != 0:
            raise Exception(f"Processing failed: {result.stderr}")
        
        # FIX: look for output file in BASE_DIR where main.py saves it
        expected_output = os.path.join(BASE_DIR, f"{base_name}_output_video.mp4")
        if not os.path.exists(expected_output):
            raise Exception(f"Output file not generated. main.py output was: {result.stdout}")
            
        # Move to outputs directory
        output_filename = f"{base_name}_{language_name}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        os.rename(expected_output, output_path)
        
        processing_status.update({
            "state": "completed",
            "progress": 100,
            "message": f"Processing completed successfully. {language_name} translation ready!",
            "output_file": output_filename
        })
        
    except Exception as e:
        processing_status.update({
            "state": "error",
            "message": f"Error: {str(e)}",
            "output_file": ""
        })
        
    finally:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass

@app.route('/status')
def get_status():
    return jsonify(processing_status)

@app.route('/download/<filename>')
def download_file(filename):
    safe_filename = secure_filename(filename)
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], safe_filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/reset', methods=['POST'])
def reset_system():
    global processing_status
    processing_status = {
        "state": "idle",
        "progress": 0,
        "message": "",
        "current_file": "",
        "output_file": "",
        "target_language": ""
    }
    return jsonify({'message': 'System reset successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)