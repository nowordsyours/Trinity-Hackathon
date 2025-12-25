"""
Data Preprocessing Utilities for AI Model
Handles cleaning, validation, and feature engineering for sensor data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self, config=None):
        """Initialize the data preprocessor"""
        self.config = config or {}
        self.scaler = None
        self.feature_columns = [
            'humidity', 'temperature', 'ammonia_level', 'co2_level',
            'occupancy_duration', 'usage_count', 'cleaning_frequency'
        ]
    
    def validate_sensor_data(self, data: pd.DataFrame) -> bool:
        """Validate sensor data for quality and consistency"""
        try:
            # Check for missing values
            missing_values = data.isnull().sum()
            if missing_values.any():
                logger.warning(f"Missing values found: {missing_values[missing_values > 0].to_dict()}")
                return False
            
            # Check data types
            for col in self.feature_columns:
                if col in data.columns:
                    if not pd.api.types.is_numeric_dtype(data[col]):
                        logger.error(f"Column {col} is not numeric")
                        return False
            
            # Check value ranges
            validation_rules = {
                'humidity': (0, 100),
                'temperature': (15, 35),
                'ammonia_level': (0, 5),
                'co2_level': (300, 1000),
                'occupancy_duration': (60, 600),
                'usage_count': (0, 50),
                'cleaning_frequency': (1, 24)
            }
            
            for col, (min_val, max_val) in validation_rules.items():
                if col in data.columns:
                    if (data[col] < min_val).any() or (data[col] > max_val).any():
                        logger.error(f"Column {col} has values outside range [{min_val}, {max_val}]")
                        return False
            
            logger.info("Data validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return False
    
    def handle_missing_values(self, data: pd.DataFrame, strategy: str = 'median') -> pd.DataFrame:
        """Handle missing values in the dataset"""
        try:
            data_cleaned = data.copy()
            
            for col in self.feature_columns:
                if col in data_cleaned.columns and data_cleaned[col].isnull().any():
                    if strategy == 'median':
                        fill_value = data_cleaned[col].median()
                    elif strategy == 'mean':
                        fill_value = data_cleaned[col].mean()
                    elif strategy == 'forward_fill':
                        data_cleaned[col] = data_cleaned[col].fillna(method='ffill')
                        continue
                    else:
                        fill_value = 0
                    
                    data_cleaned[col].fillna(fill_value, inplace=True)
                    logger.info(f"Filled missing values in {col} with {strategy}: {fill_value}")
            
            return data_cleaned
            
        except Exception as e:
            logger.error(f"Error handling missing values: {str(e)}")
            return data
    
    def remove_outliers(self, data: pd.DataFrame, method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """Remove outliers from the dataset"""
        try:
            data_cleaned = data.copy()
            
            for col in self.feature_columns:
                if col in data_cleaned.columns:
                    if method == 'iqr':
                        Q1 = data_cleaned[col].quantile(0.25)
                        Q3 = data_cleaned[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - threshold * IQR
                        upper_bound = Q3 + threshold * IQR
                        
                        outliers = (data_cleaned[col] < lower_bound) | (data_cleaned[col] > upper_bound)
                        data_cleaned = data_cleaned[~outliers]
                        
                        logger.info(f"Removed {outliers.sum()} outliers from {col}")
                    
                    elif method == 'zscore':
                        z_scores = np.abs((data_cleaned[col] - data_cleaned[col].mean()) / data_cleaned[col].std())
                        outliers = z_scores > threshold
                        data_cleaned = data_cleaned[~outliers]
                        
                        logger.info(f"Removed {outliers.sum()} outliers from {col}")
            
            return data_cleaned
            
        except Exception as e:
            logger.error(f"Error removing outliers: {str(e)}")
            return data
    
    def normalize_features(self, data: pd.DataFrame, method: str = 'minmax') -> pd.DataFrame:
        """Normalize feature values"""
        try:
            data_normalized = data.copy()
            
            if method == 'minmax':
                self.scaler = MinMaxScaler()
            elif method == 'standard':
                self.scaler = StandardScaler()
            else:
                logger.warning(f"Unknown normalization method: {method}")
                return data
            
            # Fit and transform numeric columns
            numeric_cols = [col for col in self.feature_columns if col in data.columns]
            data_normalized[numeric_cols] = self.scaler.fit_transform(data[numeric_cols])
            
            logger.info(f"Applied {method} normalization to {len(numeric_cols)} features")
            return data_normalized
            
        except Exception as e:
            logger.error(f"Error normalizing features: {str(e)}")
            return data
    
    def create_time_features(self, data: pd.DataFrame, timestamp_col: str = 'timestamp') -> pd.DataFrame:
        """Create time-based features"""
        try:
            data_with_time = data.copy()
            
            if timestamp_col in data.columns:
                data_with_time[timestamp_col] = pd.to_datetime(data_with_time[timestamp_col])
                
                # Extract time features
                data_with_time['hour'] = data_with_time[timestamp_col].dt.hour
                data_with_time['day_of_week'] = data_with_time[timestamp_col].dt.dayofweek
                data_with_time['is_weekend'] = data_with_time['day_of_week'].isin([5, 6]).astype(int)
                data_with_time['is_business_hours'] = ((data_with_time['hour'] >= 9) & 
                                                     (data_with_time['hour'] <= 17)).astype(int)
                
                logger.info("Created time-based features")
            
            return data_with_time
            
        except Exception as e:
            logger.error(f"Error creating time features: {str(e)}")
            return data
    
    def create_aggregate_features(self, data: pd.DataFrame, window_size: int = 3) -> pd.DataFrame:
        """Create aggregate features using rolling windows"""
        try:
            data_agg = data.copy()
            
            for col in self.feature_columns:
                if col in data.columns:
                    # Rolling statistics
                    data_agg[f'{col}_mean_{window_size}'] = data[col].rolling(window=window_size).mean()
                    data_agg[f'{col}_std_{window_size}'] = data[col].rolling(window=window_size).std()
                    data_agg[f'{col}_max_{window_size}'] = data[col].rolling(window=window_size).max()
                    data_agg[f'{col}_min_{window_size}'] = data[col].rolling(window=window_size).min()
            
            logger.info(f"Created aggregate features with window size {window_size}")
            return data_agg
            
        except Exception as e:
            logger.error(f"Error creating aggregate features: {str(e)}")
            return data
    
    def preprocess_pipeline(self, data: pd.DataFrame, steps: List[str] = None) -> pd.DataFrame:
        """Complete preprocessing pipeline"""
        if steps is None:
            steps = ['validate', 'handle_missing', 'remove_outliers', 'normalize']
        
        logger.info(f"Starting preprocessing pipeline with steps: {steps}")
        data_processed = data.copy()
        
        try:
            for step in steps:
                if step == 'validate':
                    if not self.validate_sensor_data(data_processed):
                        logger.error("Data validation failed")
                        return None
                
                elif step == 'handle_missing':
                    data_processed = self.handle_missing_values(data_processed)
                
                elif step == 'remove_outliers':
                    data_processed = self.remove_outliers(data_processed)
                
                elif step == 'normalize':
                    data_processed = self.normalize_features(data_processed)
                
                elif step == 'time_features':
                    data_processed = self.create_time_features(data_processed)
                
                elif step == 'aggregate_features':
                    data_processed = self.create_aggregate_features(data_processed)
                
                else:
                    logger.warning(f"Unknown preprocessing step: {step}")
            
            logger.info("Preprocessing pipeline completed successfully")
            return data_processed
            
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {str(e)}")
            return None
    
    def save_preprocessed_data(self, data: pd.DataFrame, filename: str, directory: str = 'processed'):
        """Save preprocessed data to file"""
        try:
            save_path = os.path.join(self.config.get('data_dir', 'data'), directory, filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            data.to_csv(save_path, index=False)
            logger.info(f"Saved preprocessed data to {save_path}")
            
        except Exception as e:
            logger.error(f"Error saving preprocessed data: {str(e)}")
    
    def load_preprocessed_data(self, filename: str, directory: str = 'processed'):
        """Load preprocessed data from file"""
        try:
            load_path = os.path.join(self.config.get('data_dir', 'data'), directory, filename)
            
            if os.path.exists(load_path):
                data = pd.read_csv(load_path)
                logger.info(f"Loaded preprocessed data from {load_path}")
                return data
            else:
                logger.error(f"Preprocessed data file not found: {load_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading preprocessed data: {str(e)}")
            return None

def main():
    """Example usage of the data preprocessor"""
    # Sample data
    sample_data = pd.DataFrame({
        'humidity': [65.2, 68.5, 62.1, 70.8, 64.3],
        'temperature': [22.1, 21.8, 22.3, 21.9, 22.0],
        'ammonia_level': [0.8, 1.2, 0.5, 1.8, 0.9],
        'co2_level': [450, 520, 380, 650, 480],
        'occupancy_duration': [180, 240, 120, 300, 200],
        'usage_count': [12, 15, 8, 20, 14],
        'cleaning_frequency': [8, 6, 10, 4, 7]
    })
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor()
    
    # Run preprocessing pipeline
    processed_data = preprocessor.preprocess_pipeline(sample_data)
    
    if processed_data is not None:
        print("Preprocessing completed successfully!")
        print(f"Original shape: {sample_data.shape}")
        print(f"Processed shape: {processed_data.shape}")
        print("\nFirst few rows of processed data:")
        print(processed_data.head())

if __name__ == "__main__":
    main()