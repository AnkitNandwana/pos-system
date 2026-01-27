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

def test_rapid_items():
    print("Testing Rapid Items Fraud Detection")
    print("=" * 40)
    
    # Get test employee
    employee = Employee.objects.first()
    basket_id = 'test_basket_123'
    
    # Initialize plugin
    plugin = FraudDetectionPlugin()
    print("✓ Fraud detection plugin initialized")
    
    # Clear existing alerts
    FraudAlert.objects.filter(basket_id=basket_id).delete()
    print("✓ Cleared existing alerts")
    
    # Simulate basket start
    plugin.handle_event('BASKET_STARTED', {
        'basket_id': basket_id,
        'employee_id': employee.id,
        'terminal_id': 'test-terminal',
        'timestamp': datetime.now().isoformat()
    })
    print("✓ Basket started")
    
    # Add items rapidly
    for i in range(5):
        plugin.handle_event('item.added', {
            'basket_id': basket_id,
            'product_id': f'ITEM_{i}',
            'employee_id': employee.id,
            'timestamp': datetime.now().isoformat()
        })
        print(f"✓ Added item {i+1}")
    
    # Check if alert was created
    alerts = FraudAlert.objects.filter(basket_id=basket_id)
    
    if alerts.exists():
        alert = alerts.first()
        print(f"\n🚨 FRAUD ALERT DETECTED!")
        print(f"   Rule: {alert.rule.name}")
        print(f"   Severity: {alert.severity}")
        print(f"   Details: {alert.details}")
        return True
    else:
        print("\n❌ No fraud alert was created")
        
        # Debug basket state
        from plugins.fraud_detection.state_manager import state_manager
        basket_state = state_manager.get_basket_state(basket_id)
        if basket_state:
            print(f"   Basket state found: {basket_state}")
        else:
            print("   No basket state found")
        return False

if __name__ == '__main__':
    success = test_rapid_items()
    if success:
        print("\n✅ Rapid items fraud detection test PASSED")
    else:
        print("\n❌ Rapid items fraud detection test FAILED")
        sys.exit(1)