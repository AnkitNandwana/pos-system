#!/bin/bash

echo "Manual Fraud Detection Test"
echo "=========================="

echo ""
echo "Since WebSocket connections are causing issues, let's test fraud detection manually:"
echo ""

echo "1. Start Django server:"
echo "   python manage.py runserver"
echo ""

echo "2. Start Kafka consumer:"
echo "   python manage.py consume_events"
echo ""

echo "3. Setup fraud rules:"
echo "   python manage.py setup_fraud_detection"
echo ""

echo "4. Test fraud detection via Django shell:"
echo "   python manage.py shell"
echo ""

echo "5. In Django shell, run:"
echo "   from plugins.fraud_detection.plugin import FraudDetectionPlugin"
echo "   from employees.models import Employee"
echo "   plugin = FraudDetectionPlugin()"
echo "   employee = Employee.objects.first()"
echo "   # Test multiple terminals"
echo "   plugin.handle_event('employee.login', {"
echo "       'employee_id': employee.id,"
echo "       'terminal_id': 'test-terminal-1'"
echo "   })"
echo "   plugin.handle_event('employee.login', {"
echo "       'employee_id': employee.id,"
echo "       'terminal_id': 'test-terminal-2'"
echo "   })"
echo ""

echo "6. Check fraud_alerts table:"
echo "   python manage.py shell"
echo "   from plugins.fraud_detection.models import FraudAlert"
echo "   alerts = FraudAlert.objects.all()"
echo "   for alert in alerts:"
echo "       print(f'Alert: {alert.rule.name} - {alert.severity}')"
echo ""

echo "7. For UI testing without WebSocket spam:"
echo "   - Manually trigger alerts via management command"
echo "   - Use database polling instead of WebSocket"
echo "   - Test individual components in isolation"