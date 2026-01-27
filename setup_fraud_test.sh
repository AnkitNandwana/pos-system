#!/bin/bash

# Fraud Detection Quick Setup Script
echo "🚀 Setting up Fraud Detection for Testing..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Run this script from the Django project root directory"
    exit 1
fi

# Run migrations
echo "📦 Running migrations..."
python3 manage.py migrate

# Setup fraud detection
echo "⚙️  Setting up fraud detection rules..."
python3 manage.py setup_fraud_detection

# Check setup
echo "🔍 Verifying setup..."
python3 manage.py shell -c "
from plugins.fraud_detection.models import FraudRule
from plugins.models import PluginConfiguration
from plugins.registry import plugin_registry

print('✅ Fraud Rules:', FraudRule.objects.filter(enabled=True).count())
print('✅ Plugin Config:', PluginConfiguration.objects.filter(name='fraud_detection', enabled=True).exists())
print('✅ Plugin Registered:', 'fraud_detection' in plugin_registry._plugins)

# Check if employee exists
from employees.models import Employee
if Employee.objects.filter(id=1).exists():
    emp = Employee.objects.get(id=1)
    print(f'✅ Test Employee: {emp.username}')
else:
    print('⚠️  No employee with ID 1 found. Create one for testing.')
"

echo ""
echo "🎯 Ready to test! Follow these steps:"
echo ""
echo "Terminal 1 - Start Kafka Consumer:"
echo "  python3 manage.py consume_events"
echo ""
echo "Terminal 2 - Run Flow Test:"
echo "  python3 test_fraud_flow.py"
echo ""
echo "Terminal 3 - Check Results:"
echo "  python3 manage.py runserver"
echo "  Visit: http://localhost:8000/admin/fraud_detection/"
echo ""
echo "📖 For detailed testing guide, see: FRAUD_TESTING_GUIDE.md"