import mlflow 
import mlflow.sklearn
import pickle


logreg_model = pickle.load(open('models/Fraud_transaction_logreg_model.pkl','rb'))
rf_model = pickle.load(open('models/Fraud_transaction_randomforest_model.pkl','rb'))
xgb_model = pickle.load(open('models/Fraud_transaction_xgb_model.pkl','rb'))

mlflow.set_tracking_uri("http://localhost:5000")

with mlflow.start_run():
    mlflow.sklearn.log_model(
        sk_model=logreg_model,
        artifact_path="fraud_detection_pipeline",
        registered_model_name="FraudDetection_LogisticReg"
    )
    
with mlflow.start_run():
    mlflow.sklearn.log_model(
        sk_model=rf_model,
        artifact_path="fraud_detection_pipeline",
        registered_model_name="FraudDetection_RandomForest"
    )
    
with mlflow.start_run():
    mlflow.sklearn.log_model(
        sk_model=xgb_model,
        artifact_path="fraud_detection_pipeline",
        registered_model_name="FraudDetection_XGBoost"
    )
    
    
print("Successfully registered all models")

