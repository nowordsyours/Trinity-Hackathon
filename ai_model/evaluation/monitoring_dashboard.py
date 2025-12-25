"""
Real-time Monitoring Dashboard for AI Hygiene Model
Provides live monitoring of model performance and predictions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import time
import json
import os
import logging
from collections import deque
import threading
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MonitoringDashboard:
    def __init__(self, window_size=100, alert_thresholds=None):
        """Initialize the monitoring dashboard"""
        self.window_size = window_size
        self.alert_thresholds = alert_thresholds or {
            'prediction_variance': 15.0,
            'error_rate': 10.0,
            'response_time': 2.0,
            'data_drift': 0.3
        }
        
        # Data storage for monitoring
        self.predictions_history = deque(maxlen=window_size)
        self.actual_history = deque(maxlen=window_size)
        self.errors_history = deque(maxlen=window_size)
        self.response_times_history = deque(maxlen=window_size)
        self.feature_stats_history = deque(maxlen=window_size)
        
        # Alert tracking
        self.alerts = []
        self.alert_cooldown = {}  # Prevent alert spam
        
        # Performance metrics
        self.metrics = {
            'total_predictions': 0,
            'total_errors': 0,
            'average_error': 0.0,
            'average_response_time': 0.0,
            'last_update': None
        }
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("Monitoring dashboard initialized")
    
    def log_prediction(self, prediction_data: Dict):
        """Log a new prediction for monitoring"""
        with self.lock:
            try:
                timestamp = datetime.now()
                
                # Store prediction data
                self.predictions_history.append({
                    'timestamp': timestamp,
                    'prediction': prediction_data.get('prediction'),
                    'confidence': prediction_data.get('confidence', 0.0),
                    'features': prediction_data.get('features', {})
                })
                
                # Store actual value if available
                if 'actual' in prediction_data:
                    self.actual_history.append({
                        'timestamp': timestamp,
                        'actual': prediction_data['actual']
                    })
                    
                    # Calculate error
                    error = abs(pred_data['actual'] - prediction_data['prediction'])
                    self.errors_history.append({
                        'timestamp': timestamp,
                        'error': error,
                        'percentage_error': (error / prediction_data['actual']) * 100 if prediction_data['actual'] > 0 else 0
                    })
                    
                    self.metrics['total_errors'] += error
                
                # Store response time
                if 'response_time' in prediction_data:
                    self.response_times_history.append({
                        'timestamp': timestamp,
                        'response_time': prediction_data['response_time']
                    })
                
                # Update feature statistics
                if 'features' in prediction_data:
                    self._update_feature_stats(prediction_data['features'])
                
                # Update metrics
                self.metrics['total_predictions'] += 1
                self.metrics['last_update'] = timestamp
                
                # Check for alerts
                self._check_alerts()
                
                logger.debug(f"Prediction logged: {prediction_data.get('prediction')}")
                
            except Exception as e:
                logger.error(f"Error logging prediction: {str(e)}")
    
    def _update_feature_stats(self, features: Dict):
        """Update feature statistics for drift detection"""
        try:
            feature_stats = {
                'timestamp': datetime.now(),
                'features': features,
                'feature_means': {k: np.mean(list(features.values())) for k in features.keys()},
                'feature_variance': np.var(list(features.values()))
            }
            
            self.feature_stats_history.append(feature_stats)
            
        except Exception as e:
            logger.error(f"Error updating feature stats: {str(e)}")
    
    def _check_alerts(self):
        """Check for various alert conditions"""
        current_time = datetime.now()
        
        # Check prediction variance
        if len(self.predictions_history) >= 10:
            recent_predictions = [p['prediction'] for p in list(self.predictions_history)[-10:]]
            variance = np.var(recent_predictions)
            
            if variance > self.alert_thresholds['prediction_variance']:
                self._add_alert('HIGH_PREDICTION_VARIANCE', 
                              f"High prediction variance detected: {variance:.2f}")
        
        # Check error rate
        if len(self.errors_history) >= 5:
            recent_errors = [e['percentage_error'] for e in list(self.errors_history)[-5:]]
            avg_error = np.mean(recent_errors)
            
            if avg_error > self.alert_thresholds['error_rate']:
                self._add_alert('HIGH_ERROR_RATE', 
                              f"High error rate detected: {avg_error:.1f}%")
        
        # Check response time
        if len(self.response_times_history) >= 3:
            recent_response_times = [r['response_time'] for r in list(self.response_times_history)[-3:]]
            avg_response_time = np.mean(recent_response_times)
            
            if avg_response_time > self.alert_thresholds['response_time']:
                self._add_alert('HIGH_RESPONSE_TIME', 
                              f"High response time detected: {avg_response_time:.2f}s")
        
        # Check data drift
        if len(self.feature_stats_history) >= 20:
            recent_stats = list(self.feature_stats_history)[-20:]
            older_stats = list(self.feature_stats_history)[:10]
            
            # Simple drift detection - compare feature means
            recent_means = np.array([list(s['feature_means'].values()) for s in recent_stats])
            older_means = np.array([list(s['feature_means'].values()) for s in older_stats])
            
            drift_score = np.mean(np.abs(recent_means.mean(axis=0) - older_means.mean(axis=0)))
            
            if drift_score > self.alert_thresholds['data_drift']:
                self._add_alert('DATA_DRIFT_DETECTED', 
                              f"Data drift detected: {drift_score:.3f}")
    
    def _add_alert(self, alert_type: str, message: str):
        """Add a new alert with cooldown to prevent spam"""
        current_time = datetime.now()
        
        # Check cooldown
        if alert_type in self.alert_cooldown:
            if (current_time - self.alert_cooldown[alert_type]).seconds < 300:  # 5 minute cooldown
                return
        
        alert = {
            'timestamp': current_time,
            'type': alert_type,
            'message': message,
            'severity': self._get_alert_severity(alert_type)
        }
        
        self.alerts.append(alert)
        self.alert_cooldown[alert_type] = current_time
        
        logger.warning(f"ALERT: {alert_type} - {message}")
    
    def _get_alert_severity(self, alert_type: str) -> str:
        """Get alert severity level"""
        severity_map = {
            'HIGH_PREDICTION_VARIANCE': 'MEDIUM',
            'HIGH_ERROR_RATE': 'HIGH',
            'HIGH_RESPONSE_TIME': 'MEDIUM',
            'DATA_DRIFT_DETECTED': 'HIGH'
        }
        return severity_map.get(alert_type, 'LOW')
    
    def get_current_metrics(self) -> Dict:
        """Get current performance metrics"""
        with self.lock:
            try:
                metrics = self.metrics.copy()
                
                # Calculate current averages
                if self.errors_history:
                    recent_errors = [e['error'] for e in list(self.errors_history)[-20:]]
                    metrics['current_average_error'] = np.mean(recent_errors)
                    
                    recent_pct_errors = [e['percentage_error'] for e in list(self.errors_history)[-20:]]
                    metrics['current_error_rate'] = np.mean(recent_pct_errors)
                
                if self.response_times_history:
                    recent_times = [r['response_time'] for r in list(self.response_times_history)[-10:]]
                    metrics['current_average_response_time'] = np.mean(recent_times)
                
                if self.predictions_history:
                    recent_predictions = [p['prediction'] for p in list(self.predictions_history)[-20:]]
                    metrics['current_prediction_variance'] = np.var(recent_predictions)
                    metrics['current_prediction_mean'] = np.mean(recent_predictions)
                
                return metrics
                
            except Exception as e:
                logger.error(f"Error getting current metrics: {str(e)}")
                return self.metrics
    
    def get_alerts_summary(self) -> Dict:
        """Get summary of recent alerts"""
        with self.lock:
            try:
                recent_alerts = [a for a in self.alerts 
                               if (datetime.now() - a['timestamp']).seconds < 3600]  # Last hour
                
                alert_summary = {
                    'total_alerts': len(self.alerts),
                    'recent_alerts': len(recent_alerts),
                    'alerts_by_severity': {
                        'HIGH': len([a for a in recent_alerts if a['severity'] == 'HIGH']),
                        'MEDIUM': len([a for a in recent_alerts if a['severity'] == 'MEDIUM']),
                        'LOW': len([a for a in recent_alerts if a['severity'] == 'LOW'])
                    },
                    'recent_alert_types': {}
                }
                
                # Count alert types
                for alert in recent_alerts:
                    alert_type = alert['type']
                    if alert_type not in alert_summary['recent_alert_types']:
                        alert_summary['recent_alert_types'][alert_type] = 0
                    alert_summary['recent_alert_types'][alert_type] += 1
                
                return alert_summary
                
            except Exception as e:
                logger.error(f"Error getting alerts summary: {str(e)}")
                return {'total_alerts': 0, 'recent_alerts': 0}
    
    def plot_monitoring_dashboard(self, save_path=None):
        """Create comprehensive monitoring dashboard plots"""
        try:
            fig, axes = plt.subplots(3, 2, figsize=(16, 18))
            fig.suptitle('AI Model Monitoring Dashboard', fontsize=16)
            
            # 1. Predictions over time
            ax1 = axes[0, 0]
            if self.predictions_history:
                timestamps = [p['timestamp'] for p in self.predictions_history]
                predictions = [p['prediction'] for p in self.predictions_history]
                
                ax1.plot(timestamps, predictions, 'b-', alpha=0.7)
                ax1.set_xlabel('Time')
                ax1.set_ylabel('Predicted Hygiene Score')
                ax1.set_title('Predictions Over Time')
                ax1.grid(True, alpha=0.3)
                ax1.tick_params(axis='x', rotation=45)
            else:
                ax1.text(0.5, 0.5, 'No prediction data available', 
                        ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Predictions Over Time')
            
            # 2. Error distribution
            ax2 = axes[0, 1]
            if self.errors_history:
                errors = [e['percentage_error'] for e in self.errors_history]
                
                ax2.hist(errors, bins=20, alpha=0.7, color='red', edgecolor='black')
                ax2.set_xlabel('Percentage Error (%)')
                ax2.set_ylabel('Frequency')
                ax2.set_title('Prediction Error Distribution')
                ax2.grid(True, alpha=0.3)
                
                # Add statistics
                mean_error = np.mean(errors)
                ax2.axvline(mean_error, color='darkred', linestyle='--', 
                           label=f'Mean: {mean_error:.1f}%')
                ax2.legend()
            else:
                ax2.text(0.5, 0.5, 'No error data available', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Prediction Error Distribution')
            
            # 3. Response time over time
            ax3 = axes[1, 0]
            if self.response_times_history:
                timestamps = [r['timestamp'] for r in self.response_times_history]
                response_times = [r['response_time'] for r in self.response_times_history]
                
                ax3.plot(timestamps, response_times, 'g-', alpha=0.7)
                ax3.set_xlabel('Time')
                ax3.set_ylabel('Response Time (seconds)')
                ax3.set_title('Response Time Over Time')
                ax3.grid(True, alpha=0.3)
                ax3.tick_params(axis='x', rotation=45)
                
                # Add threshold line
                ax3.axhline(y=self.alert_thresholds['response_time'], 
                           color='orange', linestyle='--', alpha=0.7, label='Alert Threshold')
                ax3.legend()
            else:
                ax3.text(0.5, 0.5, 'No response time data available', 
                        ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Response Time Over Time')
            
            # 4. Alerts timeline
            ax4 = axes[1, 1]
            if self.alerts:
                # Get alerts from last 24 hours
                cutoff_time = datetime.now() - timedelta(hours=24)
                recent_alerts = [a for a in self.alerts if a['timestamp'] > cutoff_time]
                
                if recent_alerts:
                    # Count alerts by hour
                    hourly_counts = {}
                    for alert in recent_alerts:
                        hour = alert['timestamp'].replace(minute=0, second=0, microsecond=0)
                        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
                    
                    hours = sorted(hourly_counts.keys())
                    counts = [hourly_counts[hour] for hour in hours]
                    
                    ax4.bar(hours, counts, alpha=0.7, color='purple')
                    ax4.set_xlabel('Time (Hour)')
                    ax4.set_ylabel('Number of Alerts')
                    ax4.set_title('Alerts Timeline (Last 24h)')
                    ax4.grid(True, alpha=0.3)
                    ax4.tick_params(axis='x', rotation=45)
                else:
                    ax4.text(0.5, 0.5, 'No recent alerts', 
                            ha='center', va='center', transform=ax4.transAxes)
                    ax4.set_title('Alerts Timeline (Last 24h)')
            else:
                ax4.text(0.5, 0.5, 'No alerts recorded', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Alerts Timeline (Last 24h)')
            
            # 5. Feature variance (drift detection)
            ax5 = axes[2, 0]
            if self.feature_stats_history:
                timestamps = [s['timestamp'] for s in self.feature_stats_history]
                variances = [s['feature_variance'] for s in self.feature_stats_history]
                
                ax5.plot(timestamps, variances, 'orange', alpha=0.7)
                ax5.set_xlabel('Time')
                ax5.set_ylabel('Feature Variance')
                ax5.set_title('Feature Variance Over Time (Drift Detection)')
                ax5.grid(True, alpha=0.3)
                ax5.tick_params(axis='x', rotation=45)
                
                # Add trend line
                if len(variances) > 5:
                    z = np.polyfit(range(len(variances)), variances, 1)
                    p = np.poly1d(z)
                    ax5.plot(timestamps, p(range(len(variances))), 
                           "r--", alpha=0.8, label='Trend')
                    ax5.legend()
            else:
                ax5.text(0.5, 0.5, 'No feature statistics available', 
                        ha='center', va='center', transform=ax5.transAxes)
                ax5.set_title('Feature Variance Over Time (Drift Detection)')
            
            # 6. Performance summary
            ax6 = axes[2, 1]
            current_metrics = self.get_current_metrics()
            alerts_summary = self.get_alerts_summary()
            
            # Create text summary
            summary_text = f"""
            Current Performance Summary:
            
            Total Predictions: {current_metrics.get('total_predictions', 0)}
            Current Avg Error: {current_metrics.get('current_average_error', 0):.2f}
            Current Error Rate: {current_metrics.get('current_error_rate', 0):.1f}%
            Current Avg Response: {current_metrics.get('current_average_response_time', 0):.2f}s
            
            Prediction Variance: {current_metrics.get('current_prediction_variance', 0):.2f}
            
            Alerts Summary:
            Total Alerts: {alerts_summary.get('total_alerts', 0)}
            Recent Alerts (1h): {alerts_summary.get('recent_alerts', 0)}
            High Severity: {alerts_summary.get('alerts_by_severity', {}).get('HIGH', 0)}
            Medium Severity: {alerts_summary.get('alerts_by_severity', {}).get('MEDIUM', 0)}
            """
            
            ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, 
                    fontsize=10, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
            ax6.set_title('Performance Summary')
            ax6.axis('off')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Monitoring dashboard saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating monitoring dashboard: {str(e)}")
            return None
    
    def export_monitoring_data(self, filepath: str, format='json'):
        """Export monitoring data for analysis"""
        try:
            monitoring_data = {
                'predictions_history': [
                    {
                        'timestamp': p['timestamp'].isoformat(),
                        'prediction': p['prediction'],
                        'confidence': p['confidence']
                    } for p in self.predictions_history
                ],
                'errors_history': [
                    {
                        'timestamp': e['timestamp'].isoformat(),
                        'error': e['error'],
                        'percentage_error': e['percentage_error']
                    } for e in self.errors_history
                ],
                'response_times_history': [
                    {
                        'timestamp': r['timestamp'].isoformat(),
                        'response_time': r['response_time']
                    } for r in self.response_times_history
                ],
                'alerts': [
                    {
                        'timestamp': a['timestamp'].isoformat(),
                        'type': a['type'],
                        'message': a['message'],
                        'severity': a['severity']
                    } for a in self.alerts
                ],
                'current_metrics': self.get_current_metrics(),
                'alerts_summary': self.get_alerts_summary()
            }
            
            if format.lower() == 'json':
                with open(filepath, 'w') as f:
                    json.dump(monitoring_data, f, indent=2)
            elif format.lower() == 'csv':
                # Export predictions as CSV
                if self.predictions_history:
                    df = pd.DataFrame([
                        {
                            'timestamp': p['timestamp'],
                            'prediction': p['prediction'],
                            'confidence': p['confidence']
                        } for p in self.predictions_history
                    ])
                    df.to_csv(filepath, index=False)
            
            logger.info(f"Monitoring data exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting monitoring data: {str(e)}")
            return False

def main():
    """Example usage of the monitoring dashboard"""
    # Create dashboard
    dashboard = MonitoringDashboard(window_size=50)
    
    # Simulate some predictions
    import random
    
    print("Simulating predictions...")
    for i in range(30):
        # Simulate prediction data
        prediction_data = {
            'prediction': random.uniform(30, 90),
            'confidence': random.uniform(0.7, 0.95),
            'actual': random.uniform(30, 90),  # For error calculation
            'response_time': random.uniform(0.1, 1.5),
            'features': {
                'humidity': random.uniform(40, 80),
                'temperature': random.uniform(18, 25),
                'ammonia': random.uniform(0.1, 2.0),
                'co2': random.uniform(400, 1000),
                'occupancy': random.randint(0, 10),
                'usage_count': random.randint(1, 50),
                'cleaning_freq': random.randint(1, 7)
            }
        }
        
        dashboard.log_prediction(prediction_data)
        time.sleep(0.1)  # Small delay between predictions
    
    # Display current metrics
    print("\nCurrent Metrics:")
    metrics = dashboard.get_current_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    # Display alerts summary
    print("\nAlerts Summary:")
    alerts_summary = dashboard.get_alerts_summary()
    print(f"  Total Alerts: {alerts_summary.get('total_alerts', 0)}")
    print(f"  Recent Alerts: {alerts_summary.get('recent_alerts', 0)}")
    
    # Create dashboard plots
    print("\nCreating monitoring dashboard...")
    dashboard.plot_monitoring_dashboard("monitoring_dashboard.png")
    
    # Export data
    print("Exporting monitoring data...")
    dashboard.export_monitoring_data("monitoring_data.json")
    
    print("\nMonitoring dashboard example completed!")

if __name__ == "__main__":
    main()