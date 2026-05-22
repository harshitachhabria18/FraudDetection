import pickle
import json
import os

# Build paths
MODEL_PATH = os.path.join(os.path.dirname(__file__),
                          '../../models/fraud_detection_model.pkl')

FEATURES_PATH = os.path.join(os.path.dirname(__file__),
                             '../../models/feature_columns.json')

def load_model():
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully!")
        return model
    except FileNotFoundError:
        print(f"Model file not found at: {MODEL_PATH}")
        raise
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

def load_feature_columns():
    try:
        with open(FEATURES_PATH, 'r') as f:
            feature_columns = json.load(f)
        print("Feature columns loaded successfully!")
        print(f"Features: {feature_columns}")
        return feature_columns
    except FileNotFoundError:
        print(f"Feature columns file not found at: {FEATURES_PATH}")
        raise
    except Exception as e:
        print(f"Error loading feature columns: {e}")
        raise

# Load both when server starts
model = load_model()
feature_columns = load_feature_columns()