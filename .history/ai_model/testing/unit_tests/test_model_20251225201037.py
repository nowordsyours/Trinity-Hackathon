import unittest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

class TestHygieneModel(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.model_path = os.path.join('..', '..', 'models', 'hygiene_predictor.pkl')
        self.sample_data = pd.DataFrame({
            'humidity': [65.0, 70.0, 60.0],
            'temperature': [22.0, 21.5, 22.5],
            'ammonia_level': [0.8, 1.5, 0.4],
            'co2_level': [450, 600, 350],
            'occupancy_duration': [180, 300, 120],
            'usage_count': [12, 20, 8],
            'cleaning_frequency': [8, 4, 12]
        })
    
    def test_model_exists(self):
        """Test if model file exists"""
        self.assertTrue(os.path.exists(self.model_path), "Model file should exist")
    
    def test_model_prediction(self):
        """Test model prediction functionality"""
        if os.path.exists(self.model_path):
            model = joblib.load(self.model_path)
            predictions = model.predict(self.sample_data)
            
            # Test predictions shape
            self.assertEqual(len(predictions), 3, "Should predict for 3 samples")
            
            # Test prediction range (hygiene score 0-100)
            for pred in predictions:
                self.assertGreaterEqual(pred, 0, "Prediction should be >= 0")
                self.assertLessEqual(pred, 100, "Prediction should be <= 100")
    
    def test_feature_importance(self):
        """Test model feature importance"""
        if os.path.exists(self.model_path):
            model = joblib.load(self.model_path)
            
            # Check if feature importance exists
            self.assertTrue(hasattr(model, 'feature_importances_'), 
                          "Model should have feature importances")
            
            # Check number of features
            n_features = len(model.feature_importances_)
            self.assertEqual(n_features, 7, "Should have 7 feature importances")
    
    def test_data_quality(self):
        """Test data quality checks"""
        # Test for missing values
        self.assertFalse(self.sample_data.isnull().any().any(), 
                        "Sample data should not have missing values")
        
        # Test data types
        for col in self.sample_data.columns:
            self.assertTrue(pd.api.types.is_numeric_dtype(self.sample_data[col]),
                          f"Column {col} should be numeric")

if __name__ == '__main__':
    unittest.main()