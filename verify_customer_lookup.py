#!/usr/bin/env python
"""
Test script to verify customer lookup flow is working end-to-end
Run this AFTER starting the Kafka consumer
"""
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from django.utils import timezone
from customers.models import CustomerLookupLog

def test_complete_flow():
    print("🧪 Testing Complete Customer Lookup Flow")
    print("========================================")
    
    # Clear previous logs for clean test
    initial_log_count = CustomerLookupLog.objects.count()
    print(f"📊 Initial lookup logs: {initial_log_count}")
    
    # Test customer identifier
    test_identifier = "+1234567890"
    test_basket_id = f"test_basket_{int(time.time())}"
    
    print(f"🔍 Testing with customer: {test_identifier}")
    print(f"🛒 Test basket ID: {test_basket_id}")
    
    # Publish BASKET_STARTED event
    event_data = {
        'event_type': 'BASKET_STARTED',
        'timestamp': timezone.now().isoformat(),
        'employee_id': 1,
        'basket_id': test_basket_id,
        'terminal_id': 'TERM001',
        'customer_identifier': test_identifier
    }
    
    print("📤 Publishing BASKET_STARTED event...")
    event_producer.publish(settings.KAFKA_TOPIC, event_data)
    
    # Wait for processing
    print("⏳ Waiting 3 seconds for event processing...")
    time.sleep(3)
    
    # Check results
    new_log_count = CustomerLookupLog.objects.count()
    new_logs = new_log_count - initial_log_count
    
    print(f"📊 New lookup logs: {new_logs}")
    
    if new_logs > 0:
        latest_log = CustomerLookupLog.objects.latest('request_timestamp')
        print(f"✅ SUCCESS: Customer lookup triggered!")
        print(f"   - Customer: {latest_log.customer_identifier}")
        print(f"   - Status: {latest_log.status}")
        print(f"   - Duration: {latest_log.duration_ms}ms")
        print(f"   - Basket: {latest_log.basket_id}")
        
        if latest_log.status == 'SUCCESS':
            print("🎉 Customer data should now appear in frontend!")
        else:
            print(f"❌ Lookup failed: {latest_log.error_message}")
    else:
        print("❌ FAILED: No customer lookup was triggered")
        print("💡 Make sure the Kafka consumer is running:")
        print("   python manage.py consume_events")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    test_complete_flow()