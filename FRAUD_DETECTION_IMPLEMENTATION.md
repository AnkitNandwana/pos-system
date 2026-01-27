# Fraud Detection Plugin - Implementation Guide

## Overview
The Fraud Detection plugin is a stateful, event-driven system that monitors POS activities in real-time to detect suspicious patterns and behaviors. It integrates seamlessly with the existing plugin framework and Kafka event system.

## Architecture

### Core Components
1. **FraudDetectionPlugin** - Main plugin class extending BasePlugin
2. **StateManager** - Manages in-memory state for employees, terminals, and baskets
3. **FraudRule** - Database model for configurable fraud detection rules
4. **FraudAlert** - Database model for storing fraud alerts

### Event Flow
```
POS Event → Kafka → Consumer → Plugin → State Update → Rule Evaluation → Alert Generation
```

## Installation & Setup

### 1. Files Created
```
plugins/fraud_detection/
├── __init__.py
├── apps.py
├── models.py
├── plugin.py
├── state_manager.py
├── admin.py
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── setup_fraud_detection.py
└── migrations/
    └── __init__.py
```

### 2. Configuration Updates
- Added `plugins.fraud_detection` to `INSTALLED_APPS`
- Registered plugin in `consume_events.py`
- Extended event schemas in `events/schemas.py`

### 3. Setup Commands
```bash
# Run migrations
python3 manage.py makemigrations fraud_detection
python3 manage.py migrate

# Setup default rules and plugin configuration
python3 manage.py setup_fraud_detection

# Test the plugin
python3 test_fraud_detection.py
```

## Supported Events

The plugin listens to 6 event types:
- `employee.login` - Track session starts, detect multi-terminal usage
- `basket.started` - Initialize basket tracking
- `item.added` - Monitor item velocity
- `customer.identified` - Track customer association
- `payment.completed` - Evaluate payment patterns
- `employee.logout` - Clean up session state

## Fraud Rules

### Default Rules Created

1. **Multiple Terminals** (`multiple_terminals`)
   - **Trigger**: Employee login
   - **Detection**: Same employee on ≥2 terminals within 5 minutes
   - **Severity**: HIGH

2. **Rapid Item Addition** (`rapid_items`)
   - **Trigger**: Item added
   - **Detection**: ≥10 items added within 1 minute
   - **Severity**: MEDIUM

3. **High Value Payment** (`high_value_payment`)
   - **Trigger**: Payment completed
   - **Detection**: Payment ≥$1000 within 10 minutes of login
   - **Severity**: HIGH

4. **Anonymous Payment** (`anonymous_payment`)
   - **Trigger**: Payment completed
   - **Detection**: Payment ≥$500 without customer identification
   - **Severity**: MEDIUM

5. **Rapid Checkout** (`rapid_checkout`)
   - **Trigger**: Payment completed
   - **Detection**: Basket completed within 30 seconds of creation
   - **Severity**: LOW

## State Management

### Employee Sessions
- Tracks: terminal_ids, login_time, active_baskets, total_payments
- TTL: 8 hours
- Cleanup: Automatic on logout or expiration

### Terminal States
- Tracks: current_employee_id, session_start, basket_count
- TTL: 8 hours
- Cleanup: On employee logout

### Basket States
- Tracks: employee_id, terminal_id, start_time, item_count, item_velocity, customer_identified, payment_amount
- TTL: 2 hours
- Cleanup: Automatic expiration

## Alert Generation

When a fraud rule is violated:
1. **Database Record**: Creates FraudAlert with full context
2. **Kafka Event**: Publishes `fraud.alert` event
3. **Logging**: Warning-level log with details

### Alert Event Schema
```json
{
  "event_type": "fraud.alert",
  "timestamp": "2024-01-15T10:30:00Z",
  "alert_id": "uuid",
  "rule_id": "multiple_terminals",
  "severity": "HIGH",
  "employee_id": 123,
  "terminal_id": "term-001",
  "basket_id": "basket-456",
  "details": {
    "rule_name": "Employee on Multiple Terminals",
    "threshold": 2,
    "actual_value": 3,
    "terminals": ["term-001", "term-002", "term-003"]
  },
  "metadata": {
    "plugin_version": "1.0.0",
    "detection_time": "2024-01-15T10:30:00Z"
  }
}
```

## Admin Interface

### Fraud Rules Management
- View/edit all fraud rules
- Enable/disable rules
- Adjust thresholds and time windows
- Add custom rules

### Fraud Alerts Monitoring
- View all generated alerts
- Filter by severity, employee, rule
- Read-only (alerts cannot be modified)

## Testing

### Test Script Usage
```bash
python3 test_fraud_detection.py
```

The test script simulates:
- Multiple terminal logins
- Rapid item additions
- High-value payments
- Generates sample alerts

### Manual Testing
1. Start Kafka consumer: `python3 manage.py consume_events`
2. Trigger events via GraphQL or direct event publishing
3. Monitor logs for fraud alerts
4. Check Django admin for alert records

## Performance Considerations

### Memory Management
- In-memory state with automatic cleanup
- Configurable TTL for different state types
- Emergency cleanup on memory pressure

### Scalability
- Consumer-local state (no shared state initially)
- Partition-friendly (events by employee_id)
- Future: Redis for shared state across consumers

### Error Handling
- Graceful degradation on rule evaluation failures
- Continues processing other rules if one fails
- Comprehensive logging for debugging

## Extending the Plugin

### Adding New Rules
1. Create rule in Django admin or via management command
2. Add rule logic in `_check_rule_violation()` method
3. Update `_should_evaluate_rule()` mapping
4. Test with sample events

### Custom Rule Example
```python
def _check_custom_rule(self, rule, event_data, employee_id, terminal_id, basket_id):
    """Custom fraud detection logic"""
    # Your detection logic here
    if violation_detected:
        return {
            'rule_name': rule.name,
            'threshold': rule.threshold,
            'actual_value': actual_value,
            'custom_field': custom_data
        }
    return None
```

## Integration Points

### With Existing Systems
- **Plugin Framework**: Uses BasePlugin interface
- **Kafka**: Leverages existing producer/consumer
- **Database**: Integrates with Django ORM
- **Admin**: Standard Django admin interface

### Event Publishing
- Uses existing `event_producer` singleton
- Publishes to same Kafka topic as other events
- Maintains event correlation and traceability

## Monitoring & Alerting

### Log Messages
- INFO: State updates, rule evaluations
- WARNING: Fraud alerts generated
- ERROR: Plugin failures, rule evaluation errors

### Metrics to Monitor
- Alert generation rate
- Rule evaluation performance
- State cleanup frequency
- Memory usage trends

## Security Considerations

### Data Protection
- No sensitive data in logs
- Alert details contain only necessary context
- Employee data access follows existing permissions

### Rule Configuration
- Admin-only access to fraud rules
- Audit trail for rule changes
- Version control for rule configurations

## Troubleshooting

### Common Issues
1. **No alerts generated**: Check if rules are enabled and thresholds are appropriate
2. **Memory growth**: Verify state cleanup is working
3. **Missing events**: Ensure plugin is registered and enabled
4. **Rule evaluation errors**: Check logs for specific rule failures

### Debug Commands
```bash
# Check plugin registration
python3 manage.py shell -c "from plugins.registry import plugin_registry; print(plugin_registry._plugins.keys())"

# View active rules
python3 manage.py shell -c "from plugins.fraud_detection.models import FraudRule; print(FraudRule.objects.filter(enabled=True).values_list('rule_id', flat=True))"

# Check recent alerts
python3 manage.py shell -c "from plugins.fraud_detection.models import FraudAlert; print(FraudAlert.objects.count())"
```

## Future Enhancements

### Planned Features
- Machine learning-based anomaly detection
- Real-time dashboard for fraud monitoring
- Integration with external fraud detection services
- Advanced pattern recognition algorithms

### Scalability Improvements
- Redis-based shared state for multi-consumer setups
- Horizontal scaling with consistent hashing
- Event replay capabilities for missed detections
- Performance optimization for high-volume environments

---

## Quick Start Checklist

- [ ] Run migrations: `python3 manage.py migrate`
- [ ] Setup rules: `python3 manage.py setup_fraud_detection`
- [ ] Start consumer: `python3 manage.py consume_events`
- [ ] Test plugin: `python3 test_fraud_detection.py`
- [ ] Check admin: Visit `/admin/fraud_detection/`
- [ ] Monitor logs for fraud alerts

The Fraud Detection plugin is now ready for production use with comprehensive fraud detection capabilities integrated into your POS system.