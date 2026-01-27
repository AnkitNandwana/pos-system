#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from django.utils import timezone

def test_customer_lookup_event():
    """Test customer lookup by publishing a BASKET_STARTED event"""
    
    print("🧪 Testing Customer Lookup Event Flow")
    print("=====================================")
    
    # Publish a BASKET_STARTED event with customer identifier
    event_data = {
        'event_type': 'BASKET_STARTED',
        'timestamp': timezone.now().isoformat(),
        'employee_id': 1,
        'basket_id': 'test_basket_123',
        'terminal_id': 'TERM001',
        'customer_identifier': '+1234567890'  # This should trigger customer lookup
    }
    
    print(f"📤 Publishing event: {event_data}")
    
    try:
        event_producer.publish(settings.KAFKA_TOPIC, event_data)
        print("✅ Event published successfully")
        print("🔍 Check the logs to see if customer lookup plugin processes this event")
        print("📋 You can also check customer lookup logs in the database")
        
    except Exception as e:
        print(f"❌ Failed to publish event: {e}")

if __name__ == "__main__":
    test_customer_lookup_event()