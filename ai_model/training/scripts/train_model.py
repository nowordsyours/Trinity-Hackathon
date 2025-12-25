import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def load_training_data():
    """Load and preprocess training data"""
    data_path = os.path.join('..', '..', 'data', 'processed', 'training_features.csv')
    df = pd.read_csv(data_path)
    
    # Features and target
    features = ['humidity', 'temperature', 'ammonia_level', 'co2_level', 
                'occupancy_duration', 'usage_count', 'cleaning_frequency']
    X = df[features]
    y = df['hygiene_score']
    
    return X, y

def train_hygiene_model(X, y):
    """Train the hygiene prediction model"""
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_val)
    mse = mean_squared_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)
    
    print(f"Model Performance:")
    print(f"MSE: {mse:.2f}")
    print(f"R² Score: {r2:.2f}")
    
    return model

def save_model(model):
    """Save trained model"""
    model_path = os.path.join('..', '..', 'models', 'hygiene_predictor.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    print("Loading training data...")
    X, y = load_training_data()
    
    print("Training model...")
    model = train_hygiene_model(X, y)
    
    print("Saving model...")
    save_model(model)
    
    print("Training completed!")