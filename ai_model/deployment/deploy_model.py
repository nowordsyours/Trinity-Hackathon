"""
Model Deployment Script for AI Hygiene Prediction System
Handles model packaging, environment setup, and deployment
"""

import os
import sys
import json
import shutil
import subprocess
import logging
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd

logger = logging.getLogger(__name__)

class ModelDeployment:
    def __init__(self, config_path=None):
        """Initialize model deployment"""
        self.config_path = config_path or "deployment_config.json"
        self.config = self.load_config()
        self.deployment_dir = None
        self.model_version = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def load_config(self):
        """Load deployment configuration"""
        default_config = {
            "model_path": "../models/hygiene_predictor.pkl",
            "requirements_file": "requirements.txt",
            "deployment_package_name": "hygiene_model_deployment",
            "target_environment": "production",
            "backup_models": True,
            "validate_model": True,
            "create_api": True,
            "monitoring_enabled": True,
            "deployment_targets": {
                "local": {
                    "path": "./deployed_model",
                    "create_service": False
                },
                "production": {
                    "path": "/opt/hygiene_model",
                    "create_service": True,
                    "service_name": "hygiene_model_service"
                }
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                default_config.update(loaded_config)
                logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
        
        return default_config
    
    def validate_model(self, model_path):
        """Validate the model before deployment"""
        try:
            logger.info(f"Validating model: {model_path}")
            
            # Check if model file exists
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Load and test model
            model = joblib.load(model_path)
            logger.info("Model loaded successfully")
            
            # Test prediction with sample data
            sample_features = [50, 22, 1.0, 600, 2, 15, 3]  # Sample sensor data
            prediction = model.predict([sample_features])
            logger.info(f"Test prediction successful: {prediction[0]:.2f}")
            
            # Check model type
            model_type = type(model).__name__
            logger.info(f"Model type: {model_type}")
            
            # Check if model has required methods
            required_methods = ['predict']
            for method in required_methods:
                if not hasattr(model, method):
                    raise AttributeError(f"Model missing required method: {method}")
            
            logger.info("Model validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            return False
    
    def create_deployment_package(self):
        """Create deployment package with all necessary files"""
        try:
            logger.info("Creating deployment package...")
            
            # Create temporary directory for packaging
            with tempfile.TemporaryDirectory() as temp_dir:
                package_dir = os.path.join(temp_dir, self.config['deployment_package_name'])
                os.makedirs(package_dir)
                
                # Copy model file
                model_path = self.config['model_path']
                if os.path.exists(model_path):
                    shutil.copy2(model_path, package_dir)
                    logger.info(f"Model copied: {os.path.basename(model_path)}")
                else:
                    raise FileNotFoundError(f"Model file not found: {model_path}")
                
                # Copy utility scripts
                utils_files = [
                    '../utils/model_manager.py',
                    '../utils/data_preprocessor.py'
                ]
                
                utils_dir = os.path.join(package_dir, 'utils')
                os.makedirs(utils_dir)
                
                for util_file in utils_files:
                    if os.path.exists(util_file):
                        shutil.copy2(util_file, utils_dir)
                        logger.info(f"Utility copied: {os.path.basename(util_file)}")
                
                # Copy configuration
                config_dir = os.path.join(package_dir, 'config')
                os.makedirs(config_dir)
                
                config_files = [
                    '../config/model_config.py',
                    '../config/deployment_config.json'
                ]
                
                for config_file in config_files:
                    if os.path.exists(config_file):
                        shutil.copy2(config_file, config_dir)
                        logger.info(f"Config copied: {os.path.basename(config_file)}")
                
                # Create API server script
                if self.config['create_api']:
                    self._create_api_server(package_dir)
                
                # Create monitoring script
                if self.config['monitoring_enabled']:
                    self._create_monitoring_script(package_dir)
                
                # Create requirements file
                self._create_requirements_file(package_dir)
                
                # Create deployment metadata
                self._create_deployment_metadata(package_dir)
                
                # Create deployment script
                self._create_deployment_script(package_dir)
                
                # Create ZIP package
                package_path = f"{self.config['deployment_package_name']}_{self.model_version}.zip"
                with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(package_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arc_path)
                
                logger.info(f"Deployment package created: {package_path}")
                return package_path
                
        except Exception as e:
            logger.error(f"Error creating deployment package: {str(e)}")
            return None
    
    def _create_api_server(self, package_dir):
        """Create API server script"""
        api_content = '''"""
API Server for Hygiene Prediction Model
Simple Flask API for model inference
"""

from flask import Flask, request, jsonify
import joblib
import numpy as np
import logging
from datetime import datetime
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'hygiene_predictor.pkl')
model = joblib.load(MODEL_PATH)
logger.info("Model loaded successfully")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': True
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if 'features' not in data:
            return jsonify({'error': 'Missing features'}), 400
        
        features = data['features']
        
        # Convert to numpy array
        features_array = np.array(features).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(features_array)[0]
        
        # Get prediction confidence if available
        confidence = None
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_array)[0]
            confidence = float(max(probabilities))
        
        response = {
            'prediction': float(prediction),
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Prediction made: {prediction:.2f}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed'}), 500

@app.route('/model_info', methods=['GET'])
def model_info():
    """Model information endpoint"""
    try:
        info = {
            'model_type': type(model).__name__,
            'features_count': model.n_features_ if hasattr(model, 'n_features_') else 'unknown',
            'loaded_at': datetime.now().isoformat()
        }
        
        # Add feature importances if available
        if hasattr(model, 'feature_importances_'):
            info['feature_importances'] = model.feature_importances_.tolist()
        
        return jsonify(info)
        
    except Exception as e:
        logger.error(f"Model info error: {str(e)}")
        return jsonify({'error': 'Model info unavailable'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
'''
        
        api_path = os.path.join(package_dir, 'api_server.py')
        with open(api_path, 'w') as f:
            f.write(api_content)
        
        logger.info("API server script created")
    
    def _create_monitoring_script(self, package_dir):
        """Create monitoring script"""
        monitoring_content = '''"""
Model Monitoring Script
Monitors model performance and system health
"""

import time
import requests
import logging
import json
from datetime import datetime
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelMonitor:
    def __init__(self, api_url="http://localhost:5000", check_interval=60):
        self.api_url = api_url
        self.check_interval = check_interval
        self.health_history = []
        
    def check_health(self):
        """Check API health"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.health_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'status': health_data['status']
                })
                logger.info(f"Health check passed: {health_data['status']}")
                return True
            else:
                logger.warning(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            return False
    
    def check_prediction(self):
        """Test prediction endpoint"""
        try:
            # Sample features for testing
            sample_features = [50, 22, 1.0, 600, 2, 15, 3]
            
            response = requests.post(
                f"{self.api_url}/predict",
                json={'features': sample_features},
                timeout=30
            )
            
            if response.status_code == 200:
                prediction_data = response.json()
                logger.info(f"Prediction test passed: {prediction_data['prediction']:.2f}")
                return True
            else:
                logger.warning(f"Prediction test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Prediction test error: {str(e)}")
            return False
    
    def run_monitoring(self):
        """Run continuous monitoring"""
        logger.info("Starting model monitoring...")
        
        while True:
            try:
                # Check health
                health_ok = self.check_health()
                
                # Check prediction
                pred_ok = self.check_prediction()
                
                if not health_ok or not pred_ok:
                    logger.error("Monitoring checks failed!")
                    # Here you could send alerts, restart service, etc.
                
                # Wait before next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                time.sleep(self.check_interval)

if __name__ == "__main__":
    monitor = ModelMonitor()
    monitor.run_monitoring()
'''
        
        monitoring_path = os.path.join(package_dir, 'monitor_model.py')
        with open(monitoring_path, 'w') as f:
            f.write(monitoring_content)
        
        logger.info("Monitoring script created")
    
    def _create_requirements_file(self, package_dir):
        """Create requirements file"""
        requirements = [
            "flask>=2.0.0",
            "joblib>=1.0.0",
            "numpy>=1.20.0",
            "pandas>=1.3.0",
            "scikit-learn>=1.0.0",
            "requests>=2.25.0",
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0"
        ]
        
        req_path = os.path.join(package_dir, 'requirements.txt')
        with open(req_path, 'w') as f:
            f.write('\n'.join(requirements))
        
        logger.info("Requirements file created")
    
    def _create_deployment_metadata(self, package_dir):
        """Create deployment metadata file"""
        metadata = {
            "deployment_version": self.model_version,
            "deployment_date": datetime.now().isoformat(),
            "model_type": "RandomForestRegressor",
            "target_environment": self.config['target_environment'],
            "features": ["humidity", "temperature", "ammonia", "co2", "occupancy", "usage_count", "cleaning_freq"],
            "target_variable": "hygiene_score",
            "api_endpoints": ["/health", "/predict", "/model_info"],
            "monitoring_enabled": self.config['monitoring_enabled'],
            "backup_models": self.config['backup_models']
        }
        
        metadata_path = os.path.join(package_dir, 'deployment_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Deployment metadata created")
    
    def _create_deployment_script(self, package_dir):
        """Create deployment installation script"""
        script_content = '''#!/bin/bash
# Model Deployment Installation Script

echo "Starting model deployment installation..."

# Create deployment directory
DEPLOY_DIR="/opt/hygiene_model"
sudo mkdir -p $DEPLOY_DIR

# Copy files to deployment directory
echo "Copying deployment files..."
sudo cp -r ./* $DEPLOY_DIR/

# Install Python dependencies
echo "Installing Python dependencies..."
cd $DEPLOY_DIR
sudo pip3 install -r requirements.txt

# Set permissions
sudo chmod +x api_server.py
sudo chmod +x monitor_model.py

# Create systemd service (if production)
if [ "$1" == "production" ]; then
    echo "Creating systemd service..."
    sudo tee /etc/systemd/system/hygiene_model_service.service > /dev/null <<EOF
[Unit]
Description=Hygiene Model API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/bin/python3 $DEPLOY_DIR/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable hygiene_model_service.service
    echo "Systemd service created. Start with: sudo systemctl start hygiene_model_service.service"
fi

echo "Deployment installation completed!"
echo "To start the API server: python3 api_server.py"
echo "To start monitoring: python3 monitor_model.py"
'''
        
        script_path = os.path.join(package_dir, 'install_deployment.sh')
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        logger.info("Deployment installation script created")
    
    def deploy_model(self, target_environment='local'):
        """Deploy the model to target environment"""
        try:
            logger.info(f"Starting model deployment to {target_environment}")
            
            # Generate model version
            self.model_version = datetime.now().strftime("%Y%m%d_%H%M%S")
            logger.info(f"Model version: {self.model_version}")
            
            # Validate model
            if self.config['validate_model']:
                model_path = self.config['model_path']
                if not self.validate_model(model_path):
                    logger.error("Model validation failed. Deployment aborted.")
                    return False
            
            # Backup existing models if enabled
            if self.config['backup_models'] and target_environment == 'production':
                self._backup_existing_models()
            
            # Create deployment package
            package_path = self.create_deployment_package()
            if not package_path:
                logger.error("Failed to create deployment package")
                return False
            
            # Deploy to target environment
            if target_environment == 'local':
                success = self._deploy_to_local(package_path)
            elif target_environment == 'production':
                success = self._deploy_to_production(package_path)
            else:
                logger.error(f"Unknown target environment: {target_environment}")
                return False
            
            if success:
                logger.info(f"Model deployed successfully to {target_environment}")
                logger.info(f"Deployment package: {package_path}")
                return True
            else:
                logger.error(f"Deployment to {target_environment} failed")
                return False
                
        except Exception as e:
            logger.error(f"Deployment error: {str(e)}")
            return False
    
    def _backup_existing_models(self):
        """Backup existing deployed models"""
        try:
            backup_dir = f"model_backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup current production model if exists
            prod_path = self.config['deployment_targets']['production']['path']
            if os.path.exists(prod_path):
                shutil.copytree(prod_path, backup_dir, dirs_exist_ok=True)
                logger.info(f"Existing models backed up to {backup_dir}")
            
        except Exception as e:
            logger.warning(f"Backup warning: {str(e)}")
    
    def _deploy_to_local(self, package_path):
        """Deploy to local environment"""
        try:
            target_path = self.config['deployment_targets']['local']['path']
            
            # Extract package
            with zipfile.ZipFile(package_path, 'r') as zipf:
                zipf.extractall(target_path)
            
            logger.info(f"Model deployed locally to {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Local deployment error: {str(e)}")
            return False
    
    def _deploy_to_production(self, package_path):
        """Deploy to production environment"""
        try:
            # This is a simplified version - in real deployment, you might use:
            # - Docker containers
            # - Kubernetes
            # - Cloud deployment services
            # - CI/CD pipelines
            
            logger.info("Production deployment would require additional setup")
            logger.info(f"Package ready for production: {package_path}")
            
            # For demonstration, we'll just extract to a production-like path
            target_path = self.config['deployment_targets']['production']['path']
            os.makedirs(target_path, exist_ok=True)
            
            with zipfile.ZipFile(package_path, 'r') as zipf:
                zipf.extractall(target_path)
            
            logger.info(f"Production package created at {target_path}")
            logger.info("Use install_deployment.sh for complete production setup")
            
            return True
            
        except Exception as e:
            logger.error(f"Production deployment error: {str(e)}")
            return False

def main():
    """Example usage of model deployment"""
    deployment = ModelDeployment()
    
    # Deploy to local environment
    success = deployment.deploy_model('local')
    
    if success:
        print("Model deployment completed successfully!")
        print("Next steps:")
        print("1. Start API server: python api_server.py")
        print("2. Start monitoring: python monitor_model.py")
        print("3. Test prediction: curl -X POST http://localhost:5000/predict -H 'Content-Type: application/json' -d '{\"features\": [50, 22, 1.0, 600, 2, 15, 3]}'")
    else:
        print("Model deployment failed!")

if __name__ == "__main__":
    main()