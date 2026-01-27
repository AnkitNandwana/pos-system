#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append('/home/ankit/projects/personal/pos-system')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plugins.fraud_detection.plugin import FraudDetectionPlugin
from plugins.fraud_detection.models import FraudRule, FraudAlert
from employees.models import Employee

def test_fraud_detection():
    print("Testing Fraud Detection Plugin")
    print("=" * 40)
    
    # Create test fraud rule if it doesn't exist
    rule, created = FraudRule.objects.get_or_create(
        rule_id='multiple_terminals',
        defaults={
            'name': 'Multiple Terminal Usage',
            'description': 'Detects when employee uses multiple terminals',
            'severity': 'HIGH',
            'time_window': 300,
            'threshold': 2,
            'enabled': True
        }
    )
    
    if created:
        print("✓ Created fraud rule: Multiple Terminal Usage")
    else:
        print("✓ Fraud rule already exists: Multiple Terminal Usage")
    
    # Get or create test employee
    employee, created = Employee.objects.get_or_create(
        username='test@fraud.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'CASHIER'
        }
    )
    
    if created:
        print("✓ Created test employee")
    else:
        print("✓ Using existing test employee")
    
    # Initialize plugin
    plugin = FraudDetectionPlugin()
    print("✓ Fraud detection plugin initialized")
    
    # Clear existing alerts for clean test
    FraudAlert.objects.filter(employee=employee).delete()
    print("✓ Cleared existing alerts")
    
    # Test multiple terminal login
    print("\nTesting multiple terminal detection...")
    
    # First login - should not trigger alert
    plugin.handle_event('EMPLOYEE_LOGIN', {
        'employee_id': employee.id,
        'terminal_id': 'terminal-1',
        'timestamp': datetime.now().isoformat()
    })
    print("✓ First login processed")
    
    # Second login - should trigger alert
    plugin.handle_event('EMPLOYEE_LOGIN', {
        'employee_id': employee.id,
        'terminal_id': 'terminal-2',
        'timestamp': datetime.now().isoformat()
    })
    print("✓ Second login processed")
    
    # Check if alert was created
    alerts = FraudAlert.objects.filter(employee=employee)
    
    if alerts.exists():
        alert = alerts.first()
        print(f"\n🚨 FRAUD ALERT DETECTED!")
        print(f"   Rule: {alert.rule.name}")
        print(f"   Severity: {alert.severity}")
        print(f"   Details: {alert.details}")
        print(f"   Timestamp: {alert.timestamp}")
        return True
    else:
        print("\n❌ No fraud alert was created")
        return False

if __name__ == '__main__':
    success = test_fraud_detection()
    if success:
        print("\n✅ Fraud detection test PASSED")
    else:
        print("\n❌ Fraud detection test FAILED")
        sys.exit(1)