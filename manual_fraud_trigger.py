#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plugins.fraud_detection.plugin import FraudDetectionPlugin
from plugins.fraud_detection.models import FraudAlert
from employees.models import Employee

def trigger_fraud_alert():
    print("Manually triggering fraud alert for basket_fcd76cc7")
    
    employee = Employee.objects.first()
    plugin = FraudDetectionPlugin()
    
    # Simulate basket start
    plugin.handle_event('BASKET_STARTED', {
        'basket_id': 'basket_fcd76cc7',
        'employee_id': employee.id,
        'terminal_id': 'test-terminal'
    })
    
    # Add 5 items rapidly
    for i in range(5):
        plugin.handle_event('item.added', {
            'basket_id': 'basket_fcd76cc7',
            'product_id': 'BURGER',
            'employee_id': employee.id
        })
    
    # Check alerts
    alerts = FraudAlert.objects.filter(basket_id='basket_fcd76cc7')
    print(f"Created {alerts.count()} fraud alerts")
    
    for alert in alerts:
        print(f"Alert: {alert.rule.name} - {alert.severity}")

if __name__ == '__main__':
    trigger_fraud_alert()