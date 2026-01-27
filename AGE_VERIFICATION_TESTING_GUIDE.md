# Age Verification Plugin Testing Guide

## Prerequisites Setup

### 1. Initial Setup
```bash
# Navigate to project directory
cd /home/ankit/projects/personal/pos-system

# Run migrations
python3 manage.py migrate

# Setup age verification plugin
python3 manage.py setup_age_verification

# Create superuser if not exists
python3 manage.py createsuperuser
```

### 2. Verify Setup
```bash
# Check if age-restricted products are created
python3 manage.py shell -c "
from products.models import Product
restricted = Product.objects.filter(age_restricted=True)
print(f'Age-restricted products: {restricted.count()}')
for product in restricted:
    print(f'  - {product.product_id}: {product.name} (min age: {product.minimum_age})')
"

# Check if plugin is registered
python3 manage.py shell -c "
from plugins.registry import plugin_registry
print('age_verification' in plugin_registry._plugins)
"
```

## Testing Flow

### Terminal 1: Start Kafka Consumer
```bash
# This will show all events and age verification alerts in real-time
python3 manage.py consume_events
```

### Terminal 2: Run Flow Tests
```bash
# Run comprehensive age verification test
python3 test_age_verification.py
```

### Terminal 3: Monitor Results (Optional)
```bash
# Watch age verification violations in real-time
watch -n 2 "python3 manage.py shell -c '
from plugins.age_verification.models import AgeVerificationViolation
violations = AgeVerificationViolation.objects.all().order_by(\"-timestamp\")[:5]
print(\"Recent Violations:\")
for v in violations:
    print(f\"  {v.violation_type}: {v.basket_id} - {v.timestamp}\")
'"
```

## Manual Testing Steps

### Step 1: Test Age-Restricted Item Detection
```bash
# Terminal 2: Add age-restricted items to basket
python3 -c "
import os, sys, django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from datetime import datetime
import time

# Start basket
basket_id = 'BASKET-MANUAL-001'
event_producer.publish(settings.KAFKA_TOPIC, {
    'event_type': 'basket.started',
    'employee_id': 1,
    'terminal_id': 'TERM-001',
    'basket_id': basket_id,
    'timestamp': datetime.now().isoformat()
})

# Add wine (age-restricted)
event_producer.publish(settings.KAFKA_TOPIC, {
    'event_type': 'item.added',
    'employee_id': 1,
    'terminal_id': 'TERM-001',
    'basket_id': basket_id,
    'product_id': 'WINE-001',
    'timestamp': datetime.now().isoformat()
})
print('Added wine to basket - should trigger age verification requirement')
"
```

### Step 2: Test Payment Blocking
```bash
# Terminal 2: Try payment without verification
python3 -c "
import os, sys, django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from datetime import datetime

# Try to initiate payment
event_producer.publish(settings.KAFKA_TOPIC, {
    'event_type': 'payment.initiated',
    'employee_id': 1,
    'terminal_id': 'TERM-001',
    'basket_id': 'BASKET-MANUAL-001',
    'amount': 25.99,
    'timestamp': datetime.now().isoformat()
})
print('Payment initiated - should be blocked due to unverified age-restricted items')
"
```

### Step 3: Test Age Verification Completion
```bash
# Terminal 2: Complete age verification
python3 -c "
import os, sys, django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from datetime import datetime

# Complete age verification
event_producer.publish(settings.KAFKA_TOPIC, {
    'event_type': 'age.verified',
    'employee_id': 1,
    'terminal_id': 'TERM-001',
    'basket_id': 'BASKET-MANUAL-001',
    'verifier_employee_id': 1,
    'customer_age': 25,
    'verification_method': 'ID_SCAN',
    'timestamp': datetime.now().isoformat()
})
print('Age verification completed - customer age: 25')
"
```

### Step 4: Test Successful Payment
```bash
# Terminal 2: Complete payment after verification
python3 -c "
import os, sys, django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from datetime import datetime

# Complete payment
event_producer.publish(settings.KAFKA_TOPIC, {
    'event_type': 'payment.completed',
    'employee_id': 1,
    'terminal_id': 'TERM-001',
    'basket_id': 'BASKET-MANUAL-001',
    'amount': 25.99,
    'payment_method': 'CREDIT_CARD',
    'timestamp': datetime.now().isoformat()
})
print('Payment completed successfully after age verification')
"
```

## Verification Steps

### 1. Check Age Verification States in Database
```bash
python3 manage.py shell -c "
from plugins.age_verification.models import AgeVerificationState, AgeVerificationViolation
print(f'Total verification states: {AgeVerificationState.objects.count()}')
print(f'Total violations: {AgeVerificationViolation.objects.count()}')

for state in AgeVerificationState.objects.all():
    print(f'  Basket: {state.basket_id}')
    print(f'    Requires verification: {state.requires_verification}')
    print(f'    Verification completed: {state.verification_completed}')
    print(f'    Restricted items: {len(state.restricted_items)}')
    print()
"
```

### 2. Check Django Admin
```bash
# Start Django server
python3 manage.py runserver

# Visit: http://localhost:8000/admin/
# Login and navigate to:
# - Age Verification > Age verification states
# - Age Verification > Age verification violations
# - Products > Products (check age_restricted field)
```

### 3. Monitor Kafka Consumer Logs
Look for these log patterns in Terminal 1:
```
[AGE VERIFICATION] Processing event: item.added for basket BASKET-001
[AGE VERIFICATION] Age-restricted item added: Red Wine Bottle
[AGE VERIFICATION] Payment blocked for basket BASKET-001 - verification required
🚨 AGE VERIFICATION VIOLATION: UNVERIFIED_RESTRICTED_ITEMS - Basket BASKET-001
```

## Expected Results

### Age Verification Scenarios That Should Work:

1. **Age-Restricted Item Detection** (Detection Phase)
   - Adding wine, beer, cigarettes, energy drinks triggers verification requirement
   - `age.verification.required` event published
   - Basket state updated with restricted items list

2. **Payment Blocking** (Enforcement Phase)
   - Payment initiated with unverified restricted items gets blocked
   - `age.verification.failed` event published
   - Violation record created in database

3. **Verification Completion** (Success Flow)
   - `age.verified` event marks verification as completed
   - `age.verification.completed` event published
   - Subsequent payments allowed

4. **Item Removal** (Recalculation)
   - Removing all restricted items clears verification requirement
   - Payment allowed without verification

5. **State Cleanup** (Lifecycle Management)
   - Payment completion clears basket verification state
   - Database cleaned up after successful transactions

### Normal Scenarios That Should NOT Trigger Verification:
- Adding non-restricted items (soda, regular products)
- Payment with only non-restricted items
- Empty baskets

## Age-Restricted Products Available for Testing

| Product ID | Name | Category | Min Age | Test Scenario |
|------------|------|----------|---------|---------------|
| WINE-001 | Red Wine Bottle | alcohol | 21 | High-age restriction |
| BEER-001 | Beer 6-Pack | alcohol | 21 | High-age restriction |
| TOBACCO-001 | Cigarettes | tobacco | 18 | Medium-age restriction |
| ENERGY-001 | Energy Drink | energy | 16 | Low-age restriction |
| SODA-001 | Regular Soda | beverages | - | No restriction (control) |

## Event Flow Verification

### Expected Event Sequence:
1. `basket.started` → Initialize verification state
2. `item.added` (restricted) → Publish `age.verification.required`
3. `payment.initiated` (unverified) → Publish `age.verification.failed`
4. `age.verified` → Publish `age.verification.completed`
5. `payment.initiated` (verified) → Allow payment
6. `payment.completed` → Clean up state

## Troubleshooting

### No Age Verification Alerts?
```bash
# Check if plugin is enabled
python3 manage.py shell -c "
from plugins.models import PluginConfiguration
config = PluginConfiguration.objects.get(name='age_verification')
print(f'Plugin enabled: {config.enabled}')
"

# Check if products are age-restricted
python3 manage.py shell -c "
from products.models import Product
print('Age-restricted products:')
for p in Product.objects.filter(age_restricted=True):
    print(f'  {p.product_id}: {p.name} (age: {p.minimum_age})')
"
```

### Plugin Not Working?
```bash
# Check plugin registration
python3 manage.py shell -c "
from plugins.registry import plugin_registry
print('Registered plugins:', list(plugin_registry._plugins.keys()))
print('age_verification registered:', 'age_verification' in plugin_registry._plugins)
"

# Restart consumer
# Terminal 1: Ctrl+C to stop, then restart
python3 manage.py consume_events
```

### Database Issues?
```bash
# Check if tables exist
python3 manage.py dbshell -c "
\dt age_verification*
SELECT COUNT(*) FROM age_verification_states;
SELECT COUNT(*) FROM age_verification_violations;
"
```

## Success Criteria

✅ **Test Passes If:**
- Age-restricted items trigger verification requirements
- Payment is blocked for unverified restricted items
- Age verification completion allows payment
- Violations are recorded in database
- State is cleaned up after payment completion
- Events are published correctly

✅ **Expected Output:**
```
📊 TEST RESULTS
==================================================
Verification states created: 1
Violations recorded: 1

🚨 Violations detected:
  • UNVERIFIED_RESTRICTED_ITEMS - Basket: BASKET-AGE-TEST-001
    Employee: john
    Details: {'reason': 'Payment attempted with unverified age-restricted items'}

Age-restricted products in database: 4
  • Red Wine Bottle (min age: 21)
  • Beer 6-Pack (min age: 21)
  • Cigarettes (min age: 18)
  • Energy Drink (min age: 16)

✅ Age verification flow test completed!
```

## Integration with Other Plugins

### Age Verification + Fraud Detection
- Both plugins can independently block payments
- Age verification runs before fraud detection
- Combined violations provide comprehensive compliance

### Event Priority
1. **Age Verification** (Compliance - highest priority)
2. **Fraud Detection** (Risk management)
3. **Other plugins** (Enhancement features)

Run the test script and verify all scenarios work as expected!