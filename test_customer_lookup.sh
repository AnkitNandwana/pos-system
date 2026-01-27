#!/bin/bash

echo "🔍 Testing Customer Lookup Plugin Flow"
echo "======================================"

# Test 1: Check if plugin is enabled
echo "1. Checking if Customer Lookup Plugin is enabled..."
python manage.py shell -c "
from plugins.models import PluginConfiguration
try:
    config = PluginConfiguration.objects.get(name='customer_lookup')
    print(f'Plugin enabled: {config.enabled}')
    print(f'Plugin config: {config.config}')
except PluginConfiguration.DoesNotExist:
    print('Plugin configuration not found')
"

# Test 2: Test mock API directly
echo -e "\n2. Testing mock API directly..."
curl -s "http://localhost:8000/api/mock-customer-lookup/+1234567890/" | python -m json.tool

# Test 3: Check customer lookup logs
echo -e "\n3. Checking recent customer lookup logs..."
python manage.py shell -c "
from customers.models import CustomerLookupLog
logs = CustomerLookupLog.objects.all().order_by('-request_timestamp')[:5]
for log in logs:
    print(f'{log.request_timestamp}: {log.customer_identifier} -> {log.status}')
"

# Test 4: Check if customers exist in database
echo -e "\n4. Checking customers in database..."
python manage.py shell -c "
from customers.models import Customer
customers = Customer.objects.all()
print(f'Total customers: {customers.count()}')
for customer in customers:
    print(f'  {customer.customer_id}: {customer.first_name} {customer.last_name}')
"

echo -e "\n✅ Customer Lookup Test Complete"