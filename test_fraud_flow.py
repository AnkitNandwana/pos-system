#!/usr/bin/env python3
"""
Fraud Detection Flow Test
Simulates complete POS journey with fraud scenarios
"""

import os
import sys
import django
import time
import json
from datetime import datetime

# Setup Django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from plugins.fraud_detection.models import FraudAlert
from employees.models import Employee


class FraudTestRunner:
    def __init__(self):
        self.employee_id = 1
        self.terminal_ids = ['TERM-001', 'TERM-002', 'TERM-003']
        self.basket_counter = 1
        
    def publish_event(self, event_data):
        """Publish event to Kafka"""
        print(f"📤 Publishing: {event_data['event_type']} - {event_data.get('terminal_id', 'N/A')}")
        event_producer.publish(settings.KAFKA_TOPIC, event_data)
        time.sleep(0.5)  # Small delay for processing
    
    def scenario_1_multiple_terminals(self):
        """Test multiple terminals fraud detection"""
        print("\n🚨 SCENARIO 1: Multiple Terminals Fraud")
        print("=" * 50)
        
        # Employee logs into multiple terminals quickly
        for i, terminal_id in enumerate(self.terminal_ids):
            self.publish_event({
                'event_type': 'employee.login',
                'employee_id': self.employee_id,
                'terminal_id': terminal_id,
                'timestamp': datetime.now().isoformat()
            })
            print(f"   Employee logged into {terminal_id}")
            
            if i == 1:  # After 2nd login, should trigger alert
                time.sleep(1)
                alerts = FraudAlert.objects.filter(rule__rule_id='multiple_terminals').count()
                print(f"   🔍 Alerts after {i+1} logins: {alerts}")
    
    def scenario_2_rapid_items(self):
        """Test rapid item addition fraud detection"""
        print("\n🚨 SCENARIO 2: Rapid Item Addition Fraud")
        print("=" * 50)
        
        basket_id = f"BASKET-{self.basket_counter}"
        self.basket_counter += 1
        
        # Start basket
        self.publish_event({
            'event_type': 'basket.started',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'timestamp': datetime.now().isoformat()
        })
        print(f"   Started basket: {basket_id}")
        
        # Add items rapidly (should trigger after 10 items in 1 minute)
        for i in range(15):
            self.publish_event({
                'event_type': 'item.added',
                'employee_id': self.employee_id,
                'terminal_id': self.terminal_ids[0],
                'basket_id': basket_id,
                'product_id': i + 1,
                'quantity': 1,
                'timestamp': datetime.now().isoformat()
            })
            
            if i == 9:  # After 10th item, should trigger alert
                time.sleep(1)
                alerts = FraudAlert.objects.filter(rule__rule_id='rapid_items').count()
                print(f"   🔍 Alerts after {i+1} items: {alerts}")
        
        print(f"   Added 15 items rapidly to {basket_id}")
    
    def scenario_3_high_value_payment(self):
        """Test high value payment fraud detection"""
        print("\n🚨 SCENARIO 3: High Value Payment Fraud")
        print("=" * 50)
        
        basket_id = f"BASKET-{self.basket_counter}"
        self.basket_counter += 1
        
        # Start basket
        self.publish_event({
            'event_type': 'basket.started',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # High value payment (should trigger if >$1000 within 10 minutes of login)
        self.publish_event({
            'event_type': 'payment.completed',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'amount': 1500.00,
            'payment_method': 'CREDIT_CARD',
            'timestamp': datetime.now().isoformat()
        })
        print(f"   High value payment: $1500.00 in {basket_id}")
        
        time.sleep(1)
        alerts = FraudAlert.objects.filter(rule__rule_id='high_value_payment').count()
        print(f"   🔍 High value payment alerts: {alerts}")
    
    def scenario_4_anonymous_payment(self):
        """Test anonymous high-value payment fraud detection"""
        print("\n🚨 SCENARIO 4: Anonymous High-Value Payment Fraud")
        print("=" * 50)
        
        basket_id = f"BASKET-{self.basket_counter}"
        self.basket_counter += 1
        
        # Start basket
        self.publish_event({
            'event_type': 'basket.started',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # High value payment WITHOUT customer identification
        self.publish_event({
            'event_type': 'payment.completed',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'amount': 750.00,
            'payment_method': 'CASH',
            'timestamp': datetime.now().isoformat()
        })
        print(f"   Anonymous payment: $750.00 in {basket_id} (no customer ID)")
        
        time.sleep(1)
        alerts = FraudAlert.objects.filter(rule__rule_id='anonymous_payment').count()
        print(f"   🔍 Anonymous payment alerts: {alerts}")
    
    def scenario_5_rapid_checkout(self):
        """Test rapid checkout fraud detection"""
        print("\n🚨 SCENARIO 5: Rapid Checkout Fraud")
        print("=" * 50)
        
        basket_id = f"BASKET-{self.basket_counter}"
        self.basket_counter += 1
        
        # Start basket
        self.publish_event({
            'event_type': 'basket.started',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # Immediate payment (should trigger if <30 seconds)
        self.publish_event({
            'event_type': 'payment.completed',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'amount': 50.00,
            'payment_method': 'CASH',
            'timestamp': datetime.now().isoformat()
        })
        print(f"   Rapid checkout: {basket_id} completed immediately")
        
        time.sleep(1)
        alerts = FraudAlert.objects.filter(rule__rule_id='rapid_checkout').count()
        print(f"   🔍 Rapid checkout alerts: {alerts}")
    
    def scenario_6_normal_flow(self):
        """Test normal flow (should not trigger alerts)"""
        print("\n✅ SCENARIO 6: Normal Flow (No Fraud)")
        print("=" * 50)
        
        basket_id = f"BASKET-{self.basket_counter}"
        self.basket_counter += 1
        
        # Start basket
        self.publish_event({
            'event_type': 'basket.started',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # Add items normally (few items with delays)
        for i in range(3):
            self.publish_event({
                'event_type': 'item.added',
                'employee_id': self.employee_id,
                'terminal_id': self.terminal_ids[0],
                'basket_id': basket_id,
                'product_id': i + 100,
                'quantity': 1,
                'timestamp': datetime.now().isoformat()
            })
            time.sleep(0.5)
        
        # Identify customer
        self.publish_event({
            'event_type': 'customer.identified',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'customer_id': 1,
            'timestamp': datetime.now().isoformat()
        })
        
        # Wait before payment (normal checkout time)
        time.sleep(2)
        
        # Normal payment
        self.publish_event({
            'event_type': 'payment.completed',
            'employee_id': self.employee_id,
            'terminal_id': self.terminal_ids[0],
            'basket_id': basket_id,
            'amount': 45.99,
            'payment_method': 'CREDIT_CARD',
            'timestamp': datetime.now().isoformat()
        })
        print(f"   Normal checkout: {basket_id} with customer ID, $45.99")
    
    def cleanup_session(self):
        """Logout from all terminals"""
        print("\n🔄 CLEANUP: Logging out from all terminals")
        print("=" * 50)
        
        for terminal_id in self.terminal_ids:
            self.publish_event({
                'event_type': 'employee.logout',
                'employee_id': self.employee_id,
                'terminal_id': terminal_id,
                'timestamp': datetime.now().isoformat()
            })
            print(f"   Logged out from {terminal_id}")
    
    def run_all_scenarios(self):
        """Run all fraud detection scenarios"""
        print("🎯 FRAUD DETECTION FLOW TEST")
        print("=" * 60)
        
        # Clear previous alerts
        initial_alerts = FraudAlert.objects.count()
        if initial_alerts > 0:
            FraudAlert.objects.all().delete()
            print(f"🧹 Cleared {initial_alerts} previous alerts")
        
        # Check employee exists
        try:
            employee = Employee.objects.get(id=self.employee_id)
            print(f"👤 Testing with employee: {employee.username}")
        except Employee.DoesNotExist:
            print("❌ Employee ID 1 not found. Create an employee first.")
            return
        
        print(f"⏰ Test started at: {datetime.now()}")
        print("\n" + "="*60)
        
        # Run scenarios
        self.scenario_1_multiple_terminals()
        time.sleep(2)
        
        self.scenario_2_rapid_items()
        time.sleep(2)
        
        self.scenario_3_high_value_payment()
        time.sleep(2)
        
        self.scenario_4_anonymous_payment()
        time.sleep(2)
        
        self.scenario_5_rapid_checkout()
        time.sleep(2)
        
        self.scenario_6_normal_flow()
        time.sleep(2)
        
        self.cleanup_session()
        
        # Final summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_alerts = FraudAlert.objects.count()
        print(f"Total fraud alerts generated: {total_alerts}")
        
        if total_alerts > 0:
            print("\nAlert breakdown:")
            for alert in FraudAlert.objects.all().order_by('-timestamp'):
                print(f"  🚨 {alert.rule.name} ({alert.severity})")
                print(f"     Details: {alert.details}")
                print(f"     Time: {alert.timestamp}")
                print()
        else:
            print("⚠️  No alerts generated. Check:")
            print("   - Kafka consumer is running")
            print("   - Fraud rules are enabled")
            print("   - Plugin is registered")
        
        print("="*60)


if __name__ == '__main__':
    runner = FraudTestRunner()
    runner.run_all_scenarios()