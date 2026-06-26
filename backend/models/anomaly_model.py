"""
Isolation Forest model for anomaly detection.
Trains on synthetic normal server metrics and provides inference.
"""
import joblib
import numpy as np
import os
from sklearn.ensemble import IsolationForest

# Path to save the trained model inside the models/ directory
MODEL_PATH = os.path.join(os.path.dirname(__file__), "anomaly_model.joblib")

def train_model():
    """
    Generates synthetic 'normal' server metrics and trains the Isolation Forest.
    In a real scenario, this would be trained on historical production data.
    """
    print("🧠 Training Isolation Forest on synthetic normal data...")
    
    # Generate 1000 rows of "normal" server metrics
    # Features: [cpu_usage(%), memory_usage(%), request_latency(ms), error_rate(%)]
    np.random.seed(42)
    normal_data = np.column_stack((
        np.random.normal(40, 10, 1000),   # CPU: ~40% +/- 10%
        np.random.normal(50, 10, 1000),   # Memory: ~50% +/- 10%
        np.random.normal(150, 30, 1000),  # Latency: ~150ms +/- 30ms
        np.random.normal(0.5, 0.2, 1000)  # Error Rate: ~0.5% +/- 0.2%
    ))
    
    # Train the model (contamination=0 means we assume training data is 100% normal)
    model = IsolationForest(contamination='auto', random_state=42)
    model.fit(normal_data)
    
    # Save the model to disk
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model trained and saved to {MODEL_PATH}")
    return model

def load_model():
    """Loads the trained model from disk. Trains a new one if it doesn't exist."""
    if not os.path.exists(MODEL_PATH):
        print("⚠️ Model not found. Training a new one...")
        return train_model()
    return joblib.load(MODEL_PATH)

def predict_anomaly(features: list[float]) -> dict:
    """
    Predicts if the given server metrics are anomalous.
    Returns a dictionary with the prediction result and anomaly score.
    """
    model = load_model()
    
    # Reshape for sklearn (expects 2D array)
    data_point = np.array(features).reshape(1, -1)
    
    # Predict: -1 means anomaly, 1 means normal
    prediction = model.predict(data_point)[0]
    
    # Score: The lower, the more abnormal. (Negative scores are anomalies)
    anomaly_score = model.score_samples(data_point)[0]
    
    is_anomaly = bool(prediction == -1)
    
    return {
        "is_anomaly": is_anomaly,
        "anomaly_score": float(anomaly_score),
        "features": {
            "cpu_usage": features[0],
            "memory_usage": features[1],
            "request_latency_ms": features[2],
            "error_rate": features[3]
        }
    }