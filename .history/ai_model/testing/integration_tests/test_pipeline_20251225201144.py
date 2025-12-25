import unittest
import pandas as pd
import os
import sys

# Add the training scripts to path
sys.path.append(os.path.join('..', '..', 'training', 'scripts'))

class TestPipeline(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.training_data_path = os.path.join('..', '..', 'data', 'processed', 'training_features.csv')
        self.testing_data_path = os.path.join('..', '..', 'data', 'processed', 'testing_features.csv')
    
    def test_training_data_integrity(self):
        """Test training data integrity"""
        df = pd.read_csv(self.training_data_path)
        
        # Test data shape
        self.assertGreater(len(df), 0, "Training data should not be empty")
        self.assertEqual(df.shape[1], 8, "Should have 8 columns")
        
        # Test required columns
        required_cols = ['toilet_id', 'humidity', 'temperature', 'ammonia_level', 
                        'co2_level', 'occupancy_duration', 'usage_count', 'hygiene_score']
        for col in required_cols:
            self.assertIn(col, df.columns, f"Should have column {col}")
        
        # Test data quality
        self.assertFalse(df.isnull().any().any(), "Should not have missing values")
    
    def test_testing_data_integrity(self):
        """Test testing data integrity"""
        df = pd.read_csv(self.testing_data_path)
        
        # Test data shape
        self.assertGreater(len(df), 0, "Testing data should not be empty")
        self.assertEqual(df.shape[1], 8, "Should have 8 columns")
        
        # Test required columns (no hygiene_score for testing)
        required_cols = ['toilet_id', 'humidity', 'temperature', 'ammonia_level', 
                        'co2_level', 'occupancy_duration', 'usage_count', 'cleaning_frequency']
        for col in required_cols:
            self.assertIn(col, df.columns, f"Should have column {col}")
        
        # Test data quality
        self.assertFalse(df.isnull().any().any(), "Should not have missing values")
    
    def test_data_consistency(self):
        """Test consistency between training and testing data"""
        train_df = pd.read_csv(self.training_data_path)
        test_df = pd.read_csv(self.testing_data_path)
        
        # Test feature consistency (excluding toilet_id and hygiene_score)
        train_features = set(train_df.columns) - {'toilet_id', 'hygiene_score'}
        test_features = set(test_df.columns) - {'toilet_id', 'cleaning_frequency'}
        
        self.assertEqual(train_features, test_features, "Feature sets should be consistent")
    
    def test_feature_ranges(self):
        """Test that features are within reasonable ranges"""
        df = pd.read_csv(self.training_data_path)
        
        # Test humidity range (0-100%)
        self.assertTrue((df['humidity'] >= 0).all() and (df['humidity'] <= 100).all(),
                       "Humidity should be between 0-100")
        
        # Test temperature range (15-35°C)
        self.assertTrue((df['temperature'] >= 15).all() and (df['temperature'] <= 35).all(),
                       "Temperature should be between 15-35°C")
        
        # Test hygiene score range (0-100)
        self.assertTrue((df['hygiene_score'] >= 0).all() and (df['hygiene_score'] <= 100).all(),
                       "Hygiene score should be between 0-100")

if __name__ == '__main__':
    unittest.main()