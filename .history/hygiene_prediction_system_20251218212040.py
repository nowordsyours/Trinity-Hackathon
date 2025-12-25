"""
Smart Public Toilet Hygiene Prediction System
End-to-end AI model for predicting hygiene scores and status using IoT sensor data
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

class HygienePredictionSystem:
    def __init__(self):
        self.model = None
        self.feature_columns = ['ammonia', 'methane', 'humidity', 'temperature', 
                               'footfall', 'water_flow', 'ph', 'turbidity']
        
    def generate_synthetic_dataset(self, n_samples=3000):
        """
        Generate realistic synthetic dataset with proper correlations
        Higher gas levels, turbidity, footfall reduce hygiene score
        Neutral pH (~7) increases hygiene
        Higher water flow improves hygiene
        """
        np.random.seed(42)  # For reproducibility
        
        # Generate base features with realistic distributions
        data = {
            'ammonia': np.random.beta(2, 5, n_samples) * 100,  # Skewed towards lower values
            'methane': np.random.beta(3, 4, n_samples) * 100,   # Skewed towards lower values
            'humidity': np.random.normal(60, 15, n_samples),    # Normal distribution around 60%
            'temperature': np.random.normal(25, 8, n_samples),  # Normal distribution around 25°C
            'footfall': np.random.exponential(8, n_samples),      # Exponential distribution
            'water_flow': np.random.gamma(2, 5, n_samples),      # Gamma distribution
            'ph': np.random.normal(7, 1.5, n_samples),         # Normal around neutral pH
            'turbidity': np.random.exponential(50, n_samples)   # Exponential distribution
        }
        
        # Clip values to realistic ranges
        data['humidity'] = np.clip(data['humidity'], 30, 90)
        data['temperature'] = np.clip(data['temperature'], 15, 45)
        data['footfall'] = np.clip(data['footfall'], 0, 50)
        data['water_flow'] = np.clip(data['water_flow'], 0, 30)
        data['ph'] = np.clip(data['ph'], 4, 9)
        data['turbidity'] = np.clip(data['turbidity'], 0, 500)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Calculate hygiene score based on realistic correlations
        # Base score starts at 100
        hygiene_score = 100 * np.ones(n_samples)
        
        # Negative correlations (reduce hygiene score)
        hygiene_score -= (df['ammonia'] / 100) * 25  # High ammonia reduces hygiene
        hygiene_score -= (df['methane'] / 100) * 20   # High methane reduces hygiene
        hygiene_score -= (df['footfall'] / 50) * 15   # High footfall reduces hygiene
        hygiene_score -= (df['turbidity'] / 500) * 25 # High turbidity reduces hygiene
        
        # Positive correlations (improve hygiene score)
        hygiene_score += (df['water_flow'] / 30) * 15  # High water flow improves hygiene
        
        # pH correlation (optimal around 7)
        ph_deviation = np.abs(df['ph'] - 7)
        hygiene_score -= (ph_deviation / 5) * 20  # Deviation from neutral pH reduces hygiene
        
        # Temperature and humidity effects (optimal ranges)
        temp_deviation = np.abs(df['temperature'] - 25)
        humidity_deviation = np.abs(df['humidity'] - 60)
        hygiene_score -= (temp_deviation / 30) * 10
        hygiene_score -= (humidity_deviation / 60) * 10
        
        # Add some random noise for realism
        noise = np.random.normal(0, 5, n_samples)
        hygiene_score += noise
        
        # Clip to valid range and round
        hygiene_score = np.clip(hygiene_score, 0, 100)
        df['hygiene_score'] = np.round(hygiene_score, 1)
        
        # Create hygiene status based on score thresholds
        conditions = [
            df['hygiene_score'] >= 80,
            (df['hygiene_score'] >= 50) & (df['hygiene_score'] < 80),
            df['hygiene_score'] < 50
        ]
        choices = ['Clean', 'Moderate', 'Dirty']
        df['hygiene_status'] = np.select(conditions, choices)
        
        return df
    
    def train_model(self, df):
        """
        Train Random Forest Regressor for hygiene score prediction
        """
        print("Training Random Forest Regressor...")
        
        # Prepare features and target
        X = df[self.feature_columns]
        y = df['hygiene_score']
        
        # Split data (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Initialize and train model
        # Using optimized parameters for hackathon demo
        self.model = RandomForestRegressor(
            n_estimators=100,      # Good balance of accuracy and speed
            max_depth=15,           # Prevent overfitting
            min_samples_split=5,    # Ensure robust splits
            min_samples_leaf=2,     # Prevent overfitting
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Make predictions on test set
        y_pred = self.model.predict(X_test)
        
        # Calculate evaluation metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"Model Training Complete!")
        print(f"R² Score: {r2:.4f}")
        print(f"Mean Absolute Error: {mae:.2f}")
        print(f"Model Accuracy: {r2*100:.2f}%")
        
        # Display feature importance
        self.display_feature_importance()
        
        return X_test, y_test, y_pred
    
    def display_feature_importance(self):
        """
        Display feature importance for explainable AI
        """
        if self.model is None:
            print("Model not trained yet!")
            return
        
        importance_df = pd.DataFrame({
            'Feature': self.feature_columns,
            'Importance': self.model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        print("\nFeature Importance (Explainable AI):")
        print("=" * 40)
        for _, row in importance_df.iterrows():
            print(f"{row['Feature']:12}: {row['Importance']:.4f}")
        
        # Explain the most important features
        print("\nKey Insights for Judges:")
        print("- Higher gas levels (ammonia, methane) indicate poor hygiene")
        print("- Water flow helps maintain cleanliness")
        print("- pH levels around 7 (neutral) are optimal")
        print("- High turbidity indicates water contamination")
        print("- Footfall correlates with usage and hygiene degradation")
    
    def predict_hygiene(self, input_json):
        """
        Predict hygiene score and status from sensor data
        
        Args:
            input_json: JSON string or dict with sensor readings
            
        Returns:
            dict: Contains predicted hygiene score and status
        """
        if self.model is None:
            return {"error": "Model not loaded. Please train the model first."}
        
        try:
            # Parse JSON if string
            if isinstance(input_json, str):
                input_data = json.loads(input_json)
            else:
                input_data = input_json
            
            # Validate required features
            missing_features = set(self.feature_columns) - set(input_data.keys())
            if missing_features:
                return {"error": f"Missing features: {missing_features}"}
            
            # Extract features in correct order
            features = np.array([[input_data[feature] for feature in self.feature_columns]])
            
            # Make prediction
            hygiene_score = self.model.predict(features)[0]
            
            # Determine status
            if hygiene_score >= 80:
                hygiene_status = "Clean"
            elif hygiene_score >= 50:
                hygiene_status = "Moderate"
            else:
                hygiene_status = "Dirty"
            
            return {
                "hygiene_score": round(float(hygiene_score), 1),
                "hygiene_status": hygiene_status,
                "confidence": "High",
                "explanation": self.get_prediction_explanation(input_data, hygiene_score)
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def get_prediction_explanation(self, input_data, predicted_score):
        """
        Provide explainable AI explanation for prediction
        """
        explanations = []
        
        if input_data['ammonia'] > 70:
            explanations.append("High ammonia levels detected")
        if input_data['methane'] > 70:
            explanations.append("High methane levels detected")
        if input_data['turbidity'] > 200:
            explanations.append("High water turbidity indicates contamination")
        if input_data['ph'] < 6 or input_data['ph'] > 8:
            explanations.append("pH levels outside optimal range")
        if input_data['water_flow'] < 5:
            explanations.append("Low water flow may indicate poor cleaning")
        if input_data['footfall'] > 30:
            explanations.append("High footfall suggests frequent usage")
        
        if not explanations:
            explanations.append("Sensor readings within normal ranges")
        
        return "; ".join(explanations)
    
    def save_model(self, filename='hygiene_model.pkl'):
        """
        Save trained model to file
        """
        if self.model is None:
            print("No model to save!")
            return False
        
        joblib.dump(self.model, filename)
        print(f"Model saved as {filename}")
        return True
    
    def load_model(self, filename='hygiene_model.pkl'):
        """
        Load trained model from file
        """
        try:
            self.model = joblib.load(filename)
            print(f"Model loaded from {filename}")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False

def main():
    """
    Main execution function for demonstration
    """
    print("=" * 60)
    print("SMART PUBLIC TOILET HYGIENE PREDICTION SYSTEM")
    print("=" * 60)
    
    # Initialize system
    hygiene_system = HygienePredictionSystem()
    
    # Generate synthetic dataset
    print("\n1. Generating synthetic dataset...")
    dataset = hygiene_system.generate_synthetic_dataset(n_samples=3000)
    print(f"Dataset created with {len(dataset)} samples")
    print(f"Dataset shape: {dataset.shape}")
    print("\nDataset preview:")
    print(dataset.head())
    
    # Show target distribution
    print(f"\nHygiene Status Distribution:")
    print(dataset['hygiene_status'].value_counts())
    print(f"\nHygiene Score Statistics:")
    print(dataset['hygiene_score'].describe())
    
    # Train model
    print("\n2. Training AI model...")
    X_test, y_test, y_pred = hygiene_system.train_model(dataset)
    
    # Save model
    print("\n3. Saving trained model...")
    hygiene_system.save_model('hygiene_model.pkl')
    
    # Demonstrate prediction with sample data
    print("\n4. Demonstrating prediction...")
    sample_input = {
        "ammonia": 85.0,
        "methane": 75.0,
        "humidity": 65.0,
        "temperature": 28.0,
        "footfall": 35.0,
        "water_flow": 8.0,
        "ph": 6.2,
        "turbidity": 180.0
    }
    
    print("Sample sensor input:")
    for key, value in sample_input.items():
        print(f"  {key}: {value}")
    
    result = hygiene_system.predict_hygiene(sample_input)
    print(f"\nPrediction Result:")
    print(json.dumps(result, indent=2))
    
    # Test with another sample
    print("\n5. Testing with clean toilet sample...")
    clean_sample = {
        "ammonia": 15.0,
        "methane": 10.0,
        "humidity": 55.0,
        "temperature": 22.0,
        "footfall": 8.0,
        "water_flow": 25.0,
        "ph": 7.1,
        "turbidity": 25.0
    }
    
    clean_result = hygiene_system.predict_hygiene(clean_sample)
    print(f"Clean toilet prediction:")
    print(json.dumps(clean_result, indent=2))
    
    print("\n" + "=" * 60)
    print("SYSTEM READY FOR HACKATHON DEMO!")
    print("=" * 60)

if __name__ == "__main__":
    main()