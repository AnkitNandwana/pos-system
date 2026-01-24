#!/usr/bin/env python3

import os
import sys
import django
import time
from datetime import datetime

# Setup Django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from plugins.age_verification.models import AgeVerificationState, AgeVerificationViolation
from products.models import Product


def test_age_verification_flow():
    """Test complete age verification flow"""
    print("🧪 TESTING AGE VERIFICATION PLUGIN")
    print("=" * 50)
    
    # Clear previous test data
    AgeVerificationState.objects.all().delete()
    AgeVerificationViolation.objects.all().delete()
    
    # Test data
    basket_id = 'BASKET-AGE-TEST-001'
    employee_id = 1
    terminal_id = 'TERM-001'
    
    print("📋 Test Scenario: Age-Restricted Items Flow")
    print("-" * 40)
    
    # Step 1: Start basket
    print("1. Starting basket...")
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'basket.started',
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'basket_id': basket_id,
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(1)
    
    # Step 2: Add regular item (should not trigger verification)
    print("2. Adding regular item (soda)...")
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'item.added',
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'basket_id': basket_id,
        'product_id': 'SODA-001',
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(1)
    
    # Step 3: Add age-restricted item (wine)
    print("3. Adding age-restricted item (wine)...")
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'item.added',
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'basket_id': basket_id,
        'product_id': 'WINE-001',
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(1)
    
    # Step 4: Add another age-restricted item (cigarettes)
    print("4. Adding another age-restricted item (cigarettes)...")
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'item.added',
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'basket_id': basket_id,
        'product_id': 'TOBACCO-001',
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(1)
    
    # Step 5: Try to initiate payment (should be blocked)
    print("5. Attempting payment without verification (should be blocked)...")
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'payment.initiated',
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'basket_id': basket_id,
        'amount': 34.98,
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(1)
    
    # Step 6: Complete age verification
    print("6. Completing age verification...")
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'age.verified',
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'basket_id': basket_id,
        'verifier_employee_id': employee_id,
        'customer_age': 25,
        'verification_method': 'ID_SCAN',
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(1)
    
    # Step 7: Complete payment (should succeed now)
    print("7. Completing payment after verification...")
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'payment.completed',
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'basket_id': basket_id,
        'amount': 34.98,
        'payment_method': 'CREDIT_CARD',
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    # Check verification states
    states = AgeVerificationState.objects.all()
    violations = AgeVerificationViolation.objects.all()
    
    print(f"Verification states created: {states.count()}")
    print(f"Violations recorded: {violations.count()}")
    
    if violations.exists():
        print("\n🚨 Violations detected:")
        for violation in violations:
            print(f"  • {violation.violation_type} - Basket: {violation.basket_id}")
            print(f"    Employee: {violation.employee.username}")
            print(f"    Details: {violation.details}")
    
    # Check age-restricted products
    restricted_products = Product.objects.filter(age_restricted=True)
    print(f"\nAge-restricted products in database: {restricted_products.count()}")
    for product in restricted_products:
        print(f"  • {product.name} (min age: {product.minimum_age})")
    
    print("\n✅ Age verification flow test completed!")
    print("Check the Kafka consumer logs for detailed event processing.")


def test_item_removal_flow():
    """Test item removal recalculation"""
    print("\n🧪 TESTING ITEM REMOVAL FLOW")
    print("=" * 50)
    
    basket_id = 'BASKET-REMOVAL-TEST'
    employee_id = 1
    terminal_id = 'TERM-001'
    
    # Start basket and add restricted item
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'basket.started',
        'basket_id': basket_id,
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(0.5)
    
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'item.added',
        'basket_id': basket_id,
        'product_id': 'BEER-001',
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(0.5)
    
    # Remove the restricted item
    print("Removing age-restricted item...")
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'item.removed',
        'basket_id': basket_id,
        'product_id': 'BEER-001',
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(1)
    
    # Try payment (should succeed without verification)
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'payment.initiated',
        'basket_id': basket_id,
        'employee_id': employee_id,
        'terminal_id': terminal_id,
        'amount': 5.99,
        'timestamp': datetime.now().isoformat()
    })
    time.sleep(1)
    
    print("✅ Item removal test completed!")


if __name__ == '__main__':
    try:
        test_age_verification_flow()
        test_item_removal_flow()
        
        print("\n" + "🎉" * 20)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎉" * 20)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()