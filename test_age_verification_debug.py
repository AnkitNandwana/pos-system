#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from baskets.models import Basket, BasketItem
from employees.models import Employee
from products.models import Product
from events.producer import event_producer
from django.conf import settings
from django.utils import timezone

def test_age_verification():
    print("🧪 Testing Age Verification System")
    print("=" * 50)
    
    # Get or create employee
    try:
        employee = Employee.objects.first()
        if not employee:
            print("❌ No employees found. Please create an employee first.")
            return
        print(f"✅ Using employee: {employee.username}")
    except Exception as e:
        print(f"❌ Error getting employee: {e}")
        return
    
    # Create a test basket
    try:
        basket = Basket.objects.create(
            basket_id="test_basket_123",
            employee=employee
        )
        print(f"✅ Created test basket: {basket.basket_id}")
    except Exception as e:
        print(f"❌ Error creating basket: {e}")
        return
    
    # Test with age-restricted product
    try:
        age_restricted_product = Product.objects.filter(age_restricted=True).first()
        if not age_restricted_product:
            print("❌ No age-restricted products found")
            return
            
        print(f"✅ Testing with age-restricted product: {age_restricted_product.name}")
        
        # Simulate adding age-restricted item
        event_data = {
            'event_type': 'item.added',
            'timestamp': timezone.now().isoformat(),
            'basket_id': basket.basket_id,
            'product_id': age_restricted_product.product_id,
            'product_name': age_restricted_product.name,
            'quantity': 1,
            'price': float(age_restricted_product.price),
            'employee_id': employee.id,
            'age_restricted': True
        }
        
        print("📤 Publishing age-restricted item event...")
        event_producer.publish(settings.KAFKA_TOPIC, event_data)
        print("✅ Event published successfully!")
        
        print("\n🔍 Check the Kafka consumer logs to see if the age verification plugin processes this event.")
        print("You should see logs like:")
        print("  [AGE VERIFICATION] Processing item.added event...")
        print("  [AGE VERIFICATION] Published verification required event...")
        
    except Exception as e:
        print(f"❌ Error testing age-restricted product: {e}")
    
    # Cleanup
    try:
        basket.delete()
        print("🧹 Cleaned up test basket")
    except Exception as e:
        print(f"⚠️  Error cleaning up: {e}")

if __name__ == "__main__":
    test_age_verification()