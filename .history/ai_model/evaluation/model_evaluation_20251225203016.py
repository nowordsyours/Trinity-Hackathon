"""
Model Evaluation and Performance Monitoring
Comprehensive evaluation of AI model performance for hygiene prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.model_selection import cross_val_score, learning_curve
import joblib
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self, model_path=None, output_dir=None):
        """Initialize the model evaluator"""
        self.model_path = model_path
        self.output_dir = output_dir or os.path.dirname(os.path.abspath(__file__))
        self.model = None
        self.results = {}
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_model(self, model_path=None):
        """Load the trained model"""
        if model_path:
            self.model_path = model_path
        
        if not self.model_path or not os.path.exists(self.model_path):
            logger.error(f"Model file not found: {self.model_path}")
            return False
        
        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def evaluate_regression_metrics(self, y_true, y_pred):
        """Calculate regression metrics"""
        try:
            metrics = {
                'mse': mean_squared_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'mae': mean_absolute_error(y_true, y_pred),
                'r2': r2_score(y_true, y_pred),
                'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            }
            
            # Calculate percentage within different error ranges
            abs_errors = np.abs(y_true - y_pred)
            metrics['within_5_points'] = np.mean(abs_errors <= 5) * 100
            metrics['within_10_points'] = np.mean(abs_errors <= 10) * 100
            metrics['within_15_points'] = np.mean(abs_errors <= 15) * 100
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating regression metrics: {str(e)}")
            return None
    
    def evaluate_classification_metrics(self, y_true, y_pred, thresholds=None):
        """Convert regression to classification and calculate metrics"""
        if thresholds is None:
            thresholds = [30, 70]  # Poor: <30, Fair: 30-70, Good: >70
        
        try:
            # Convert continuous scores to categories
            def score_to_category(score):
                if score < thresholds[0]:
                    return 'Poor'
                elif score < thresholds[1]:
                    return 'Fair'
                else:
                    return 'Good'
            
            y_true_cat = [score_to_category(score) for score in y_true]
            y_pred_cat = [score_to_category(score) for score in y_pred]
            
            # Calculate classification metrics
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            metrics = {
                'accuracy': accuracy_score(y_true_cat, y_pred_cat),
                'precision_macro': precision_score(y_true_cat, y_pred_cat, average='macro'),
                'recall_macro': recall_score(y_true_cat, y_pred_cat, average='macro'),
                'f1_macro': f1_score(y_true_cat, y_pred_cat, average='macro'),
                'precision_weighted': precision_score(y_true_cat, y_pred_cat, average='weighted'),
                'recall_weighted': recall_score(y_true_cat, y_pred_cat, average='weighted'),
                'f1_weighted': f1_score(y_true_cat, y_pred_cat, average='weighted')
            }
            
            # Classification report
            report = classification_report(y_true_cat, y_pred_cat, output_dict=True)
            metrics['classification_report'] = report
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating classification metrics: {str(e)}")
            return None
    
    def cross_validate_model(self, X, y, cv_folds=5):
        """Perform cross-validation"""
        try:
            if self.model is None:
                logger.error("No model loaded for cross-validation")
                return None
            
            # Cross-validation for regression
            cv_scores = cross_val_score(self.model, X, y, cv=cv_folds, 
                                        scoring='neg_mean_squared_error')
            
            cv_metrics = {
                'cv_mse_mean': -cv_scores.mean(),
                'cv_mse_std': cv_scores.std(),
                'cv_rmse_mean': np.sqrt(-cv_scores.mean()),
                'cv_scores': cv_scores
            }
            
            logger.info(f"Cross-validation completed: MSE={cv_metrics['cv_mse_mean']:.2f} (±{cv_metrics['cv_mse_std']:.2f})")
            return cv_metrics
            
        except Exception as e:
            logger.error(f"Error during cross-validation: {str(e)}")
            return None
    
    def plot_prediction_analysis(self, y_true, y_pred, save_path=None):
        """Create comprehensive prediction analysis plots"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Model Prediction Analysis', fontsize=16)
            
            # 1. Actual vs Predicted scatter plot
            ax1 = axes[0, 0]
            ax1.scatter(y_true, y_pred, alpha=0.6, color='blue')
            ax1.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
            ax1.set_xlabel('Actual Hygiene Score')
            ax1.set_ylabel('Predicted Hygiene Score')
            ax1.set_title('Actual vs Predicted Values')
            ax1.grid(True, alpha=0.3)
            
            # Add R² score to plot
            r2 = r2_score(y_true, y_pred)
            ax1.text(0.05, 0.95, f'R² = {r2:.3f}', transform=ax1.transAxes, 
                    bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.5))
            
            # 2. Residuals plot
            ax2 = axes[0, 1]
            residuals = y_true - y_pred
            ax2.scatter(y_pred, residuals, alpha=0.6, color='green')
            ax2.axhline(y=0, color='r', linestyle='--')
            ax2.set_xlabel('Predicted Values')
            ax2.set_ylabel('Residuals')
            ax2.set_title('Residuals Plot')
            ax2.grid(True, alpha=0.3)
            
            # 3. Error distribution
            ax3 = axes[1, 0]
            ax3.hist(residuals, bins=30, alpha=0.7, color='orange', edgecolor='black')
            ax3.set_xlabel('Prediction Error')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Error Distribution')
            ax3.grid(True, alpha=0.3)
            
            # 4. Feature importance (if available)
            ax4 = axes[1, 1]
            if hasattr(self.model, 'feature_importances_'):
                features = ['Humidity', 'Temperature', 'Ammonia', 'CO2', 
                           'Occupancy', 'Usage Count', 'Cleaning Freq']
                importances = self.model.feature_importances_
                
                # Sort features by importance
                sorted_idx = np.argsort(importances)[::-1]
                
                ax4.bar(range(len(importances)), importances[sorted_idx], color='purple', alpha=0.7)
                ax4.set_xlabel('Features')
                ax4.set_ylabel('Importance')
                ax4.set_title('Feature Importance')
                ax4.set_xticks(range(len(importances)))
                ax4.set_xticklabels([features[i] for i in sorted_idx], rotation=45)
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'Feature importance\nnot available', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Feature Importance')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Prediction analysis plot saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating prediction analysis plots: {str(e)}")
            return None
    
    def plot_learning_curves(self, X, y, save_path=None):
        """Plot learning curves to analyze model performance vs training size"""
        try:
            if self.model is None:
                logger.error("No model loaded for learning curves")
                return None
            
            # Calculate learning curves
            train_sizes, train_scores, val_scores = learning_curve(
                self.model, X, y, cv=5, n_jobs=-1,
                train_sizes=np.linspace(0.1, 1.0, 10),
                scoring='neg_mean_squared_error'
            )
            
            # Calculate mean and std
            train_scores_mean = -train_scores.mean(axis=1)
            train_scores_std = train_scores.std(axis=1)
            val_scores_mean = -val_scores.mean(axis=1)
            val_scores_std = val_scores.std(axis=1)
            
            # Create plot
            plt.figure(figsize=(10, 6))
            plt.plot(train_sizes, train_scores_mean, 'o-', color='blue', label='Training Score')
            plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                           train_scores_mean + train_scores_std, alpha=0.1, color='blue')
            
            plt.plot(train_sizes, val_scores_mean, 'o-', color='red', label='Validation Score')
            plt.fill_between(train_sizes, val_scores_mean - val_scores_std,
                           val_scores_mean + val_scores_std, alpha=0.1, color='red')
            
            plt.xlabel('Training Set Size')
            plt.ylabel('Mean Squared Error')
            plt.title('Learning Curves')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Learning curves plot saved to {save_path}")
            
            return plt.gcf()
            
        except Exception as e:
            logger.error(f"Error creating learning curves: {str(e)}")
            return None
    
    def generate_evaluation_report(self, X_test, y_test, save_path=None):
        """Generate comprehensive evaluation report"""
        try:
            if self.model is None:
                logger.error("No model loaded for evaluation")
                return None
            
            # Make predictions
            y_pred = self.model.predict(X_test)
            
            # Calculate metrics
            regression_metrics = self.evaluate_regression_metrics(y_test, y_pred)
            classification_metrics = self.evaluate_classification_metrics(y_test, y_pred)
            cv_metrics = self.cross_validate_model(X_test, y_test)
            
            # Create report
            report = {
                'timestamp': datetime.now().isoformat(),
                'model_path': self.model_path,
                'regression_metrics': regression_metrics,
                'classification_metrics': classification_metrics,
                'cross_validation_metrics': cv_metrics,
                'sample_size': len(y_test),
                'prediction_range': {
                    'min': float(y_pred.min()),
                    'max': float(y_pred.max()),
                    'mean': float(y_pred.mean()),
                    'std': float(y_pred.std())
                }
            }
            
            # Save report
            if save_path:
                import json
                with open(save_path, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                logger.info(f"Evaluation report saved to {save_path}")
            
            # Generate plots
            plots_dir = os.path.join(self.output_dir, 'plots')
            os.makedirs(plots_dir, exist_ok=True)
            
            pred_plot_path = os.path.join(plots_dir, 'prediction_analysis.png')
            self.plot_prediction_analysis(y_test, y_pred, pred_plot_path)
            
            learning_plot_path = os.path.join(plots_dir, 'learning_curves.png')
            self.plot_learning_curves(X_test, y_test, learning_plot_path)
            
            self.results = report
            return report
            
        except Exception as e:
            logger.error(f"Error generating evaluation report: {str(e)}")
            return None
    
    def print_summary(self):
        """Print evaluation summary"""
        if not self.results:
            logger.error("No evaluation results available")
            return
        
        print("\n" + "="*60)
        print("MODEL EVALUATION SUMMARY")
        print("="*60)
        print(f"Model: {self.results['model_path']}")
        print(f"Evaluation Time: {self.results['timestamp']}")
        print(f"Sample Size: {self.results['sample_size']}")
        
        if 'regression_metrics' in self.results and self.results['regression_metrics']:
            metrics = self.results['regression_metrics']
            print(f"\nREGRESSION METRICS:")
            print(f"  MSE: {metrics['mse']:.2f}")
            print(f"  RMSE: {metrics['rmse']:.2f}")
            print(f"  MAE: {metrics['mae']:.2f}")
            print(f"  R²: {metrics['r2']:.3f}")
            print(f"  MAPE: {metrics['mape']:.2f}%")
            print(f"  Accuracy within 5 points: {metrics['within_5_points']:.1f}%")
            print(f"  Accuracy within 10 points: {metrics['within_10_points']:.1f}%")
            print(f"  Accuracy within 15 points: {metrics['within_15_points']:.1f}%")
        
        if 'cross_validation_metrics' in self.results and self.results['cross_validation_metrics']:
            cv_metrics = self.results['cross_validation_metrics']
            print(f"\nCROSS-VALIDATION METRICS:")
            print(f"  CV MSE: {cv_metrics['cv_mse_mean']:.2f} (±{cv_metrics['cv_mse_std']:.2f})")
            print(f"  CV RMSE: {cv_metrics['cv_rmse_mean']:.2f}")
        
        print("\n" + "="*60)

def main():
    """Example usage of the model evaluator"""
    # Sample data for testing
    from sklearn.datasets import make_regression
    from sklearn.model_selection import train_test_split
    
    # Generate sample data
    X, y = make_regression(n_samples=1000, n_features=7, noise=10, random_state=42)
    y = (y - y.min()) / (y.max() - y.min()) * 100  # Scale to 0-100
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train a simple model
    from sklearn.ensemble import RandomForestRegressor
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    # Save model temporarily
    temp_model_path = "temp_model.pkl"
    joblib.dump(model, temp_model_path)
    
    # Evaluate model
    evaluator = ModelEvaluator(temp_model_path)
    
    if evaluator.load_model():
        report = evaluator.generate_evaluation_report(X_test, y_test, "evaluation_report.json")
        
        if report:
            evaluator.print_summary()
            print("\nEvaluation completed successfully!")
        else:
            print("Evaluation failed!")
    
    # Clean up
    if os.path.exists(temp_model_path):
        os.remove(temp_model_path)

if __name__ == "__main__":
    main()