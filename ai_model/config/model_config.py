"""
Configuration settings for the AI Hygiene Prediction Model
"""

import os

# Model Configuration
MODEL_CONFIG = {
    'model_type': 'RandomForestRegressor',
    'model_params': {
        'n_estimators': 100,
        'random_state': 42,
        'max_depth': 10,
        'min_samples_split': 5,
        'min_samples_leaf': 2
    },
    'model_name': 'hygiene_predictor.pkl',
    'backup_model_name': 'hygiene_predictor_backup.pkl'
}

# Data Configuration
DATA_CONFIG = {
    'features': [
        'humidity',
        'temperature', 
        'ammonia_level',
        'co2_level',
        'occupancy_duration',
        'usage_count',
        'cleaning_frequency'
    ],
    'target': 'hygiene_score',
    'test_size': 0.2,
    'random_state': 42,
    'validation_split': 0.2
}

# Feature Ranges and Validation
FEATURE_RANGES = {
    'humidity': {'min': 0, 'max': 100, 'unit': '%'},
    'temperature': {'min': 15, 'max': 35, 'unit': '°C'},
    'ammonia_level': {'min': 0, 'max': 5, 'unit': 'ppm'},
    'co2_level': {'min': 300, 'max': 1000, 'unit': 'ppm'},
    'occupancy_duration': {'min': 60, 'max': 600, 'unit': 'seconds'},
    'usage_count': {'min': 0, 'max': 50, 'unit': 'count'},
    'cleaning_frequency': {'min': 1, 'max': 24, 'unit': 'times/day'},
    'hygiene_score': {'min': 0, 'max': 100, 'unit': 'score'}
}

# Model Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    'mse_max': 25.0,  # Maximum acceptable Mean Squared Error
    'r2_min': 0.7,    # Minimum acceptable R² score
    'mae_max': 4.0,   # Maximum acceptable Mean Absolute Error
    'accuracy_min': 0.85  # Minimum acceptable accuracy
}

# Training Configuration
TRAINING_CONFIG = {
    'batch_size': 32,
    'max_epochs': 100,
    'early_stopping_patience': 10,
    'learning_rate': 0.01,
    'validation_frequency': 5
}

# Paths Configuration
PATHS = {
    'base_dir': os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data_dir': 'data',
    'models_dir': 'models',
    'logs_dir': 'training/logs',
    'config_dir': 'config'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_name': 'ai_model.log',
    'max_file_size': 10485760,  # 10MB
    'backup_count': 5
}

# Real-time Prediction Configuration
REALTIME_CONFIG = {
    'prediction_interval': 10,  # seconds between predictions
    'confidence_threshold': 0.8,  # minimum confidence for predictions
    'anomaly_detection': True,
    'auto_retrain': True,
    'retrain_interval': 86400  # 24 hours in seconds
}

# IoT Integration Configuration
IOT_CONFIG = {
    'sensor_data_timeout': 300,  # 5 minutes
    'max_missing_readings': 3,
    'data_validation': True,
    'fallback_model': 'backup_model'
}

# Model Deployment Configuration
DEPLOYMENT_CONFIG = {
    'model_version': '1.0.0',
    'api_endpoint': '/api/predict/hygiene',
    'timeout': 30,  # seconds
    'max_concurrent_requests': 100,
    'caching_enabled': True,
    'cache_ttl': 300  # 5 minutes
}

# Health Monitoring Configuration
HEALTH_CONFIG = {
    'health_check_interval': 60,  # seconds
    'model_drift_threshold': 0.1,
    'performance_degradation_threshold': 0.05,
    'alert_enabled': True,
    'notification_channels': ['email', 'slack']
}