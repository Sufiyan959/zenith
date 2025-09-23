import os
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ----------------- Yield Prediction -----------------
def get_yield_prediction(features_dict):
    """
    Predicts crop yield using the saved yield_predictor.pkl model.
    """
    model_path = os.path.join(BASE_DIR, 'models', 'ML_models', 'yield_predictor.pkl')
    df = pd.DataFrame([features_dict])
    model = joblib.load(model_path)
    prediction = model.predict(df)[0]
    return prediction


# ----------------- Crop Recommendation -----------------
def get_crop_recommendation(features_list):
    """
    Recommends a crop using the saved crop_model.pkl model.
    
    features_list: list of numeric features
    """
    model_path = os.path.join(BASE_DIR, 'models', 'ML_models', 'Crop_recommendation.pkl')
    model = joblib.load(model_path)
    df = pd.DataFrame([features_list])
    prediction = model.predict(df)[0]
    return crops[prediction+1]


# ----------------- Fertilizer Recommendation -----------------
def get_fertilizer_recommendation(num_features, cat_features):
    """
    Recommends fertilizer using the saved fertilizer_model.pkl model.
    
    num_features: list of numeric features [N, P, K, temperature, humidity, ph, rainfall]
    cat_features: list of categorical features [Soil Type, Crop Type]
    """
    model_path = os.path.join(BASE_DIR, 'models', 'ML_models', 'fertilizer.pkl')
    model = joblib.load(model_path)
    
    combined_features = np.array(num_features + cat_features).reshape(1, -1)
    df = pd.DataFrame(combined_features)
    
    prediction = model.predict(df)[0]
    return fertilizer_classes[prediction]


# ----------------- Lists -----------------
crops = ['apple', 'banana', 'blackgram', 'chickpea', 'coconut', 'coffee', 'cotton', 'grapes', 
         'jute', 'kidneybeans', 'lentil', 'maize', 'mango', 'mothbeans', 'mungbean', 'muskmelon', 
         'orange', 'papaya', 'pigeonpeas', 'pomegranate', 'rice', 'watermelon']

soil_types = ['Black', 'Clayey', 'Loamy', 'Red', 'Sandy']
Crop_types = ['Barley', 'Cotton', 'Ground Nuts', 'Maize', 'Millets', 'Oil seeds', 'Paddy', 
              'Pulses', 'Sugarcane', 'Tobacco', 'Wheat']
fertilizer_classes = ['10-26-26', '14-35-14', '17-17-17', '20-20', '28-28', 'DAP', 'Urea']
