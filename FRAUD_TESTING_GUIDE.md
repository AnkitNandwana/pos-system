# Fraud Detection Flow Testing Guide

## Prerequisites Setup

### 1. Initial Setup
```bash
# Navigate to project directory
cd /home/ankit/projects/personal/pos-system

# Run migrations
python3 manage.py migrate

# Setup fraud detection rules
python3 manage.py setup_fraud_detection

# Create superuser if not exists
python3 manage.py createsuperuser
```

### 2. Verify Setup
```bash
# Check if fraud rules are created
python3 manage.py shell -c "
from plugins.fraud_detection.models import FraudRule
print('Fraud Rules:', FraudRule.objects.filter(enabled=True).count())
for rule in FraudRule.objects.all():
    print(f'  - {rule.rule_id}: {rule.name} (threshold: {rule.threshold})')
"

# Check if plugin is registered
python3 manage.py shell -c "
from plugins.registry import plugin_registry
print('Registered plugins:', list(plugin_registry._plugins.keys()))
"
```

## Testing Flow

### Terminal 1: Start Kafka Consumer
```bash
# This will show all events and fraud alerts in real-time
python3 manage.py consume_events
```

### Terminal 2: Run Flow Tests
```bash
# Run comprehensive flow test
python3 test_fraud_flow.py
```

### Terminal 3: Monitor Results (Optional)
```bash
# Watch fraud alerts in real-time
watch -n 2 "python3 manage.py shell -c '
from plugins.fraud_detection.models import FraudAlert
alerts = FraudAlert.objects.all().order_by(\"-timestamp\")[:5]
print(\"Recent Alerts:\")
for alert in alerts:
    print(f\"  {alert.rule.name}: {alert.severity} - {alert.timestamp}\")
'"
```

## Manual Testing Steps

### Step 1: Multiple Terminals Fraud
```bash
# Terminal 2: Simulate multiple logins
python3 -c "
import os, sys, django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from datetime import datetime
import time

# Login to multiple terminals
terminals = ['TERM-001', 'TERM-002', 'TERM-003']
for terminal in terminals:
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'employee.login',
        'employee_id': 1,
        'terminal_id': terminal,
        'timestamp': datetime.now().isoformat()
    })
    print(f'Logged into {terminal}')
    time.sleep(1)
"
```

### Step 2: Rapid Item Addition
```bash
# Terminal 2: Simulate rapid item addition
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
basket_id = 'BASKET-TEST-001'
event_producer.publish(settings.KAFKA_TOPIC, {
    'event_type': 'basket.started',
    'employee_id': 1,
    'terminal_id': 'TERM-001',
    'basket_id': basket_id,
    'timestamp': datetime.now().isoformat()
})

# Add 15 items rapidly
for i in range(15):
    event_producer.publish(settings.KAFKA_TOPIC, {
        'event_type': 'item.added',
        'employee_id': 1,
        'terminal_id': 'TERM-001',
        'basket_id': basket_id,
        'product_id': i + 1,
        'timestamp': datetime.now().isoformat()
    })
    print(f'Added item {i+1}')
    time.sleep(0.1)
"
```

### Step 3: High Value Payment
```bash
# Terminal 2: Simulate high value payment
python3 -c "
import os, sys, django
sys.path.append('/home/ankit/projects/personal/pos-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.producer import event_producer
from django.conf import settings
from datetime import datetime

# High value payment
event_producer.publish(settings.KAFKA_TOPIC, {
    'event_type': 'payment.completed',
    'employee_id': 1,
    'terminal_id': 'TERM-001',
    'basket_id': 'BASKET-HIGH-VALUE',
    'amount': 1500.00,
    'payment_method': 'CREDIT_CARD',
    'timestamp': datetime.now().isoformat()
})
print('High value payment completed: $1500')
"
```

## Verification Steps

### 1. Check Fraud Alerts in Database
```bash
python3 manage.py shell -c "
from plugins.fraud_detection.models import FraudAlert
print(f'Total alerts: {FraudAlert.objects.count()}')
for alert in FraudAlert.objects.all():
    print(f'  {alert.rule.name}: {alert.severity}')
    print(f'    Employee: {alert.employee.username}')
    print(f'    Details: {alert.details}')
    print()
"
```

### 2. Check Django Admin
```bash
# Start Django server
python3 manage.py runserver

# Visit: http://localhost:8000/admin/
# Login and navigate to:
# - Fraud Detection > Fraud rules
# - Fraud Detection > Fraud alerts
```

### 3. Monitor Kafka Consumer Logs
Look for these log patterns in Terminal 1:
```
[FRAUD DETECTION] Processing event: employee.login
[FRAUD DETECTION] State updated for employee 1
[FRAUD DETECTION] Rule violation detected: multiple_terminals
🚨 FRAUD ALERT: Employee on Multiple Terminals - Employee john - {...}
```

## Expected Results

### Fraud Scenarios That Should Trigger Alerts:

1. **Multiple Terminals** (HIGH severity)
   - Triggers when employee logs into ≥2 terminals within 5 minutes
   - Expected: Alert after 2nd terminal login

2. **Rapid Items** (MEDIUM severity)
   - Triggers when ≥10 items added within 1 minute
   - Expected: Alert after 10th item

3. **High Value Payment** (HIGH severity)
   - Triggers when payment ≥$1000 within 10 minutes of login
   - Expected: Alert on $1500 payment

4. **Anonymous Payment** (MEDIUM severity)
   - Triggers when payment ≥$500 without customer ID
   - Expected: Alert on $750 anonymous payment

5. **Rapid Checkout** (LOW severity)
   - Triggers when basket completed within 30 seconds
   - Expected: Alert on immediate checkout

### Normal Scenarios That Should NOT Trigger Alerts:
- Single terminal login
- Normal item addition pace
- Payments with customer identification
- Reasonable checkout times

## Troubleshooting

### No Alerts Generated?
```bash
# Check if consumer is running
ps aux | grep consume_events

# Check if rules are enabled
python3 manage.py shell -c "
from plugins.fraud_detection.models import FraudRule
print('Enabled rules:', FraudRule.objects.filter(enabled=True).count())
"

# Check if plugin is registered
python3 manage.py shell -c "
from plugins.registry import plugin_registry
print('fraud_detection' in plugin_registry._plugins)
"

# Check recent events in Kafka consumer logs
tail -f /path/to/consumer/logs
```

### Plugin Not Working?
```bash
# Restart consumer
# Terminal 1: Ctrl+C to stop, then restart
python3 manage.py consume_events

# Check for errors in Django logs
python3 manage.py shell -c "
import logging
logging.basicConfig(level=logging.DEBUG)
"
```

### Database Issues?
```bash
# Check if tables exist
python3 manage.py dbshell -c "
\dt fraud_*
SELECT COUNT(*) FROM fraud_rules;
SELECT COUNT(*) FROM fraud_alerts;
"
```

## Success Criteria

✅ **Test Passes If:**
- Kafka consumer shows fraud detection events
- 5+ fraud alerts are generated
- Alerts appear in Django admin
- Different severity levels are triggered
- Normal flow doesn't generate alerts

✅ **Expected Output:**
```
📊 TEST SUMMARY
Total fraud alerts generated: 5
Alert breakdown:
  🚨 Employee on Multiple Terminals (HIGH)
  🚨 Rapid Item Addition (MEDIUM)  
  🚨 High Value Payment in Short Session (HIGH)
  🚨 Anonymous High-Value Payment (MEDIUM)
  🚨 Rapid Basket Checkout (LOW)
```

Run the flow test and verify all scenarios work as expected!