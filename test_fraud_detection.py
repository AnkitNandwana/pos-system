#!/usr/bin/env python3
"""
Test script for Fraud Detection Plugin
Simulates various fraud scenarios to test the plugin functionality
"""

import os
import sys
import django
from datetime import datetime
import json

# Setup Django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plugins.fraud_detection.plugin import FraudDetectionPlugin
from plugins.fraud_detection.models import FraudRule, FraudAlert
from employees.models import Employee


def test_multiple_terminals():
    """Test multiple terminals fraud detection"""
    print("\n=== Testing Multiple Terminals Fraud Detection ===")
    
    plugin = FraudDetectionPlugin()
    
    # Simulate employee login on multiple terminals
    events = [
        {
            'event_type': 'employee.login',
            'employee_id': 1,
            'terminal_id': 'term-001',
            'timestamp': datetime.now().isoformat()
        },
        {
            'event_type': 'employee.login',
            'employee_id': 1,
            'terminal_id': 'term-002',
            'timestamp': datetime.now().isoformat()
        },
        {
            'event_type': 'employee.login',
            'employee_id': 1,
            'terminal_id': 'term-003',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    for event in events:
        print(f"Processing: {event['event_type']} on {event['terminal_id']}")
        plugin.handle_event(event['event_type'], event)
    
    # Check if alert was created
    alerts = FraudAlert.objects.filter(rule__rule_id='multiple_terminals').count()
    print(f"Alerts created: {alerts}")


def test_rapid_items():
    """Test rapid item addition fraud detection"""
    print("\n=== Testing Rapid Item Addition Fraud Detection ===")
    
    plugin = FraudDetectionPlugin()
    
    # Start basket
    plugin.handle_event('basket.started', {
        'event_type': 'basket.started',
        'employee_id': 1,
        'terminal_id': 'term-001',
        'basket_id': 'basket-001',
        'timestamp': datetime.now().isoformat()
    })
    
    # Add items rapidly
    for i in range(15):
        plugin.handle_event('item.added', {
            'event_type': 'item.added',
            'employee_id': 1,
            'terminal_id': 'term-001',
            'basket_id': 'basket-001',
            'product_id': i + 1,
            'timestamp': datetime.now().isoformat()
        })
    
    alerts = FraudAlert.objects.filter(rule__rule_id='rapid_items').count()
    print(f"Alerts created: {alerts}")


def test_high_value_payment():
    """Test high value payment fraud detection"""
    print("\n=== Testing High Value Payment Fraud Detection ===")
    
    plugin = FraudDetectionPlugin()
    
    # Employee login
    plugin.handle_event('employee.login', {
        'event_type': 'employee.login',
        'employee_id': 1,
        'terminal_id': 'term-001',
        'timestamp': datetime.now().isoformat()
    })
    
    # High value payment
    plugin.handle_event('payment.completed', {
        'event_type': 'payment.completed',
        'employee_id': 1,
        'terminal_id': 'term-001',
        'basket_id': 'basket-002',
        'amount': 1500.00,
        'timestamp': datetime.now().isoformat()
    })
    
    alerts = FraudAlert.objects.filter(rule__rule_id='high_value_payment').count()
    print(f"Alerts created: {alerts}")


def main():
    print("Fraud Detection Plugin Test Suite")
    print("=" * 50)
    
    # Check if rules exist
    rules_count = FraudRule.objects.filter(enabled=True).count()
    print(f"Active fraud rules: {rules_count}")
    
    if rules_count == 0:
        print("No fraud rules found. Run: python3 manage.py setup_fraud_detection")
        return
    
    # Clear previous alerts for clean testing
    FraudAlert.objects.all().delete()
    print("Cleared previous alerts")
    
    # Run tests
    test_multiple_terminals()
    test_rapid_items()
    test_high_value_payment()
    
    # Summary
    total_alerts = FraudAlert.objects.count()
    print(f"\n=== Test Summary ===")
    print(f"Total alerts generated: {total_alerts}")
    
    for alert in FraudAlert.objects.all():
        print(f"- {alert.rule.name}: {alert.severity}")


if __name__ == '__main__':
    main()