#!/usr/bin/env python
"""
Test script to verify customer lookup plugin integration
"""
import os
import sys
import django
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from events.producer import event_producer
from django.conf import settings
from baskets.models import Basket
from customers.models import Customer
from employees.models import Employee
from plugins.models import PluginConfiguration

def test_customer_lookup_flow():
    print("🧪 Testing Customer Lookup Plugin Integration")
    print("=" * 50)
    
    # Check if plugin is enabled
    try:
        plugin_config = PluginConfiguration.objects.get(name='customer_lookup')
        print(f"✅ Plugin Status: {'ENABLED' if plugin_config.enabled else 'DISABLED'}")
        print(f"📋 Plugin Config: {plugin_config.config}")
    except PluginConfiguration.DoesNotExist:
        print("❌ Customer lookup plugin not configured!")
        return
    
    # Get or create test employee
    employee, _ = Employee.objects.get_or_create(
        username='test_cashier',
        defaults={
            'first_name': 'Test',
            'last_name': 'Cashier',
            'role': 'CASHIER'
        }
    )
    
    # Test customer identifier (exists in mock API)
    customer_identifier = '+1234567890'
    basket_id = f"test_basket_{int(time.time())}"
    
    print(f"\n🛒 Creating basket with customer identifier: {customer_identifier}")
    
    # Create basket manually (simulating GraphQL mutation)
    basket = Basket.objects.create(
        basket_id=basket_id,
        employee=employee,
        customer_id=customer_identifier  # This will be updated by plugin
    )
    
    print(f"📦 Created basket: {basket_id}")
    
    # Publish basket.started event (this should trigger customer lookup)
    event_data = {
        'event_type': 'basket.started',
        'timestamp': timezone.now().isoformat(),
        'employee_id': employee.id,
        'basket_id': basket_id,
        'terminal_id': 'TEST_TERMINAL',
        'customer_identifier': customer_identifier
    }
    
    print(f"\n📡 Publishing basket.started event...")
    event_producer.publish(settings.KAFKA_TOPIC, event_data)
    print(f"✅ Event published to Kafka topic: {settings.KAFKA_TOPIC}")
    
    print(f"\n⏳ Waiting for plugin to process event (5 seconds)...")
    time.sleep(5)
    
    # Check if customer was created/updated
    try:
        customer = Customer.objects.get(identifier=customer_identifier)
        print(f"\n✅ Customer found in database:")
        print(f"   Customer ID: {customer.customer_id}")
        print(f"   Name: {customer.first_name} {customer.last_name}")
        print(f"   Email: {customer.email}")
        print(f"   Tier: {customer.tier}")
        print(f"   Loyalty Points: {customer.loyalty_points}")
    except Customer.DoesNotExist:
        print(f"\n❌ Customer not found in database!")
        return
    
    # Check if basket was updated
    basket.refresh_from_db()
    if basket.customer_id == customer.customer_id:
        print(f"✅ Basket updated with customer ID: {customer.customer_id}")
    else:
        print(f"❌ Basket not updated. Current customer_id: {basket.customer_id}")
    
    print(f"\n🎉 Test completed!")
    print(f"📊 Summary:")
    print(f"   - Plugin: {'WORKING' if basket.customer_id == customer.customer_id else 'NOT WORKING'}")
    print(f"   - Customer Lookup: {'SUCCESS' if customer else 'FAILED'}")
    print(f"   - Basket Update: {'SUCCESS' if basket.customer_id == customer.customer_id else 'FAILED'}")

if __name__ == '__main__':
    test_customer_lookup_flow()