# AI Model for Smart Toilet Hygiene Monitoring

This directory contains the complete AI model infrastructure for the Smart Toilet Hygiene Monitoring System.

## Directory Structure

```
ai_model/
├── data/                    # Data storage and processing
│   ├── raw/                # Raw sensor data from IoT devices
│   ├── processed/          # Cleaned and preprocessed data
│   └── synthetic/          # Augmented and synthetic data
├── models/                 # Trained ML models and artifacts
├── training/               # Model training infrastructure
│   ├── scripts/           # Training scripts and notebooks
│   └── logs/              # Training logs and metrics
├── testing/               # Testing and validation
│   ├── unit_tests/        # Unit tests for model components
│   └── integration_tests/ # End-to-end pipeline tests
├── evaluation/            # Model evaluation and performance metrics
├── utils/                 # Utility functions and helpers
└── config/                # Configuration files and parameters

## Quick Start

### 1. Training the Model
```bash
cd training/scripts
python train_model.py
```

### 2. Running Tests
```bash
# Unit tests
cd testing/unit_tests
python test_model.py

# Integration tests
cd testing/integration_tests
python test_pipeline.py
```

### 3. Data Flow
1. **Raw Data Collection**: IoT sensors collect environmental data
2. **Data Processing**: Clean and preprocess sensor readings
3. **Model Training**: Train hygiene prediction models
4. **Model Testing**: Validate model performance
5. **Deployment**: Deploy trained models to production

## Data Format

### Training Features
- `humidity`: Relative humidity percentage (0-100)
- `temperature`: Temperature in Celsius (15-35°C)
- `ammonia_level`: Ammonia concentration (ppm)
- `co2_level`: CO2 concentration (ppm)
- `occupancy_duration`: Average occupancy time (seconds)
- `usage_count`: Number of toilet uses
- `cleaning_frequency`: Cleaning frequency per day
- `hygiene_score`: Target variable (0-100)

### Testing Features
Same as training features but without the target variable (`hygiene_score`).

## Model Architecture

The current implementation uses:
- **Algorithm**: Random Forest Regressor
- **Features**: 7 environmental and usage metrics
- **Target**: Hygiene score (0-100)
- **Evaluation**: MSE, R² Score

## Performance Metrics

- **MSE**: Mean Squared Error
- **R² Score**: Coefficient of determination
- **Feature Importance**: Ranking of input features

## File Descriptions

### Data Files
- `sensor_readings.csv`: Raw sensor data from IoT devices
- `training_features.csv`: Preprocessed training data
- `testing_features.csv`: Preprocessed testing data
- `augmented_data.csv`: Synthetic and augmented training data

### Training Scripts
- `train_model.py`: Main training script with model pipeline

### Test Files
- `test_model.py`: Unit tests for model functionality
- `test_pipeline.py`: Integration tests for data pipeline

## Usage Examples

### Loading and Using the Model
```python
import joblib
import pandas as pd

# Load trained model
model = joblib.load('models/hygiene_predictor.pkl')

# Prepare input data
input_data = pd.DataFrame({
    'humidity': [65.0],
    'temperature': [22.0],
    'ammonia_level': [0.8],
    'co2_level': [450],
    'occupancy_duration': [180],
    'usage_count': [12],
    'cleaning_frequency': [8]
})

# Make prediction
hygiene_score = model.predict(input_data)
print(f"Predicted hygiene score: {hygiene_score[0]:.1f}")
```

### Data Preprocessing
```python
import pandas as pd

def preprocess_sensor_data(raw_data):
    """Preprocess raw sensor data for model input"""
    # Handle missing values
    processed_data = raw_data.fillna(method='forward_fill')
    
    # Normalize features if needed
    # Add feature engineering logic here
    
    return processed_data
```

## Configuration

Model configuration files are stored in the `config/` directory:
- Model hyperparameters
- Feature engineering settings
- Evaluation metrics configuration

## Testing Strategy

1. **Unit Tests**: Test individual model components
2. **Integration Tests**: Test complete data pipeline
3. **Performance Tests**: Monitor model performance metrics
4. **Data Quality Tests**: Validate input data integrity

## Future Enhancements

- [ ] Deep learning models (LSTM, CNN)
- [ ] Real-time model updates
- [ ] Advanced feature engineering
- [ ] Model explainability tools
- [ ] Automated hyperparameter tuning
- [ ] Model versioning and A/B testing

## Dependencies

- pandas
- numpy
- scikit-learn
- joblib
- pytest (for testing)

## Contributing

1. Add new training data to `data/raw/`
2. Update preprocessing scripts in `training/scripts/`
3. Run tests to ensure model quality
4. Update documentation and metrics

## License

This AI model is part of the Smart Toilet Hygiene Monitoring System.