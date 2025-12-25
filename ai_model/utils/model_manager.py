"""
AI Model Manager for Smart Toilet Hygiene Monitoring System
This script manages the AI model lifecycle including training, testing, and deployment.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HygieneModelManager:
    def __init__(self, base_path=None):
        """Initialize the model manager with base path"""
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.base_path, 'data')
        self.models_path = os.path.join(self.base_path, 'models')
        self.training_path = os.path.join(self.base_path, 'training')
        self.testing_path = os.path.join(self.base_path, 'testing')
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.data_path,
            os.path.join(self.data_path, 'raw'),
            os.path.join(self.data_path, 'processed'),
            os.path.join(self.data_path, 'synthetic'),
            self.models_path,
            self.training_path,
            os.path.join(self.training_path, 'scripts'),
            os.path.join(self.training_path, 'logs'),
            self.testing_path,
            os.path.join(self.testing_path, 'unit_tests'),
            os.path.join(self.testing_path, 'integration_tests')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_training_data(self, filename='training_features.csv'):
        """Load training data from processed data folder"""
        data_file = os.path.join(self.data_path, 'processed', filename)
        
        if not os.path.exists(data_file):
            logger.error(f"Training data file not found: {data_file}")
            return None, None
        
        try:
            df = pd.read_csv(data_file)
            
            # Define features and target
            features = ['humidity', 'temperature', 'ammonia_level', 'co2_level', 
                       'occupancy_duration', 'usage_count', 'cleaning_frequency']
            
            X = df[features]
            y = df['hygiene_score']
            
            logger.info(f"Loaded training data: {len(df)} samples, {len(features)} features")
            return X, y
            
        except Exception as e:
            logger.error(f"Error loading training data: {str(e)}")
            return None, None
    
    def train_model(self, X, y, model_name='hygiene_predictor.pkl'):
        """Train the hygiene prediction model"""
        try:
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_val)
            mse = mean_squared_error(y_val, y_pred)
            r2 = r2_score(y_val, y_pred)
            
            logger.info(f"Model Performance:")
            logger.info(f"MSE: {mse:.2f}")
            logger.info(f"R² Score: {r2:.2f}")
            
            # Save model
            model_path = os.path.join(self.models_path, model_name)
            joblib.dump(model, model_path)
            logger.info(f"Model saved to {model_path}")
            
            return model, {'mse': mse, 'r2': r2}
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return None, None
    
    def load_model(self, model_name='hygiene_predictor.pkl'):
        """Load a trained model"""
        model_path = os.path.join(self.models_path, model_name)
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return None
        
        try:
            model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return None
    
    def predict_hygiene_score(self, model, sensor_data):
        """Predict hygiene score from sensor data"""
        try:
            # Ensure sensor_data is in the right format
            if isinstance(sensor_data, dict):
                sensor_data = pd.DataFrame([sensor_data])
            
            # Make prediction
            prediction = model.predict(sensor_data)
            return prediction[0]
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return None
    
    def get_model_info(self, model):
        """Get model information and feature importances"""
        try:
            if hasattr(model, 'feature_importances_'):
                features = ['humidity', 'temperature', 'ammonia_level', 'co2_level', 
                           'occupancy_duration', 'usage_count', 'cleaning_frequency']
                
                importances = model.feature_importances_
                feature_importance = dict(zip(features, importances))
                
                return {
                    'feature_importance': feature_importance,
                    'n_features': len(features),
                    'model_type': type(model).__name__
                }
            else:
                return {'model_type': type(model).__name__}
                
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return None
    
    def validate_data_quality(self, data):
        """Validate input data quality"""
        try:
            # Check for missing values
            if data.isnull().any().any():
                logger.warning("Data contains missing values")
                return False
            
            # Check data ranges
            if 'humidity' in data.columns:
                if not ((data['humidity'] >= 0).all() and (data['humidity'] <= 100).all()):
                    logger.error("Humidity values out of range (0-100)")
                    return False
            
            if 'temperature' in data.columns:
                if not ((data['temperature'] >= 15).all() and (data['temperature'] <= 35).all()):
                    logger.error("Temperature values out of range (15-35°C)")
                    return False
            
            if 'hygiene_score' in data.columns:
                if not ((data['hygiene_score'] >= 0).all() and (data['hygiene_score'] <= 100).all()):
                    logger.error("Hygiene score values out of range (0-100)")
                    return False
            
            logger.info("Data quality validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating data quality: {str(e)}")
            return False

def main():
    """Main function for testing the model manager"""
    # Initialize manager
    manager = HygieneModelManager()
    
    # Load training data
    X, y = manager.load_training_data()
    
    if X is not None and y is not None:
        # Validate data quality
        if manager.validate_data_quality(pd.concat([X, y], axis=1)):
            # Train model
            model, metrics = manager.train_model(X, y)
            
            if model is not None:
                # Get model info
                info = manager.get_model_info(model)
                print(f"Model trained successfully!")
                print(f"Performance: MSE={metrics['mse']:.2f}, R²={metrics['r2']:.2f}")
                print(f"Feature Importance: {info['feature_importance']}")
                
                # Test prediction
                sample_data = {
                    'humidity': 65.0,
                    'temperature': 22.0,
                    'ammonia_level': 0.8,
                    'co2_level': 450,
                    'occupancy_duration': 180,
                    'usage_count': 12,
                    'cleaning_frequency': 8
                }
                
                prediction = manager.predict_hygiene_score(model, sample_data)
                print(f"Sample prediction: {prediction:.1f}")

if __name__ == "__main__":
    main()