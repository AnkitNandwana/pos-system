# Fraud Detection Plugin Integration

## Overview
The fraud detection plugin monitors POS transactions in real-time and alerts cashiers when suspicious activities are detected. The system uses WebSocket connections to provide immediate notifications.

## Architecture

```
Frontend (React) ←→ WebSocket ←→ Django Channels ←→ Fraud Detection Plugin
                                        ↓
                                   Kafka Events
```

## Backend Components

### 1. Fraud Detection Plugin (`plugins/fraud_detection/plugin.py`)
- Monitors multiple event types: login, basket operations, payments
- Evaluates fraud rules in real-time
- Creates alerts and sends WebSocket notifications

### 2. WebSocket Consumer (`plugins/fraud_detection/consumers.py`)
- Handles real-time fraud alert delivery
- Manages terminal-specific alert channels
- Supports alert acknowledgment

### 3. Models (`plugins/fraud_detection/models.py`)
- `FraudRule`: Configurable fraud detection rules
- `FraudAlert`: Alert records with acknowledgment tracking

## Frontend Components

### 1. Fraud Detection Hook (`hooks/useFraudDetection.ts`)
- Manages WebSocket connection for fraud alerts
- Handles reconnection and error recovery
- Triggers callbacks when alerts are received

### 2. Fraud Alert Dialog (`components/FraudAlertDialog.tsx`)
- Displays fraud alerts with severity indicators
- Shows detailed violation information
- Provides acknowledgment functionality

## Fraud Detection Rules

### 1. Multiple Terminals
- **Trigger**: Employee login from multiple terminals
- **Threshold**: 2+ simultaneous sessions
- **Severity**: HIGH

### 2. Rapid Item Addition
- **Trigger**: Items added too quickly to basket
- **Threshold**: 5+ items in 30 seconds
- **Severity**: MEDIUM

### 3. High Value Payment (Short Session)
- **Trigger**: Large payment shortly after login
- **Threshold**: $500+ within 60 seconds of login
- **Severity**: HIGH

### 4. Anonymous High-Value Payment
- **Trigger**: Large payment without customer identification
- **Threshold**: $300+ without customer lookup
- **Severity**: MEDIUM

### 5. Rapid Checkout
- **Trigger**: Basket completed too quickly
- **Threshold**: Start to payment in < 30 seconds
- **Severity**: LOW

## Testing Scenarios

### Setup
1. Run fraud detection setup: `python manage.py setup_fraud_detection`
2. Start Django server: `python manage.py runserver`
3. Start Kafka consumer: `python manage.py consume_events`
4. Open frontend: `http://localhost:3000`

### Test Cases

#### Scenario 1: Multiple Terminal Detection
1. Login with same employee in two browser tabs
2. Expected: Fraud alert appears in first tab
3. Acknowledge alert to dismiss

#### Scenario 2: Rapid Item Addition
1. Start a new basket
2. Quickly add 5+ items (< 5 seconds between additions)
3. Expected: Fraud alert for rapid item addition
4. Acknowledge alert

#### Scenario 3: High-Value Short Session
1. Login to terminal
2. Immediately start basket and add expensive items ($500+)
3. Complete payment within 60 seconds of login
4. Expected: Fraud alert for suspicious high-value transaction

#### Scenario 4: Anonymous Payment
1. Start basket without customer lookup
2. Add items totaling $300+
3. Complete payment
4. Expected: Fraud alert for anonymous high-value payment

#### Scenario 5: Rapid Checkout
1. Start basket
2. Add items and complete payment within 30 seconds
3. Expected: Fraud alert for rapid checkout

### Manual Testing
```bash
# Trigger test alert
python manage.py trigger_fraud_alert <terminal_id> --severity HIGH

# View test scenarios
./test_fraud_detection.sh
```

## Alert Severity Levels

- **CRITICAL**: Immediate attention required (red)
- **HIGH**: Suspicious activity detected (orange)
- **MEDIUM**: Unusual pattern identified (yellow)
- **LOW**: Minor anomaly detected (blue)

## Monitoring and Logging

### Browser Console
- WebSocket connection status
- Alert reception logs
- Connection errors

### Django Logs
- Fraud rule evaluations
- Alert creation events
- Plugin execution status

### Database
- `fraud_rules`: Rule configurations
- `fraud_alerts`: Alert history and acknowledgments

## Configuration

### Fraud Rules Setup
Rules are configured via Django admin or management commands:
```python
FraudRule.objects.create(
    rule_id='custom_rule',
    name='Custom Fraud Rule',
    description='Detects custom suspicious behavior',
    severity='HIGH',
    time_window=60,
    threshold=100,
    enabled=True
)
```

### WebSocket Configuration
- Endpoint: `ws://localhost:8000/ws/fraud-alerts/{terminal_id}/`
- Authentication: Terminal-based routing
- Reconnection: Automatic with 3-second delay

## Error Handling

### Frontend
- WebSocket connection failures
- Alert parsing errors
- Automatic reconnection

### Backend
- Rule evaluation exceptions
- Alert creation failures
- Channel layer errors

## Security Considerations

- Terminal-specific alert channels
- Alert acknowledgment tracking
- Audit trail for all fraud events
- Secure WebSocket connections

## Performance

- Real-time alert delivery (< 1 second)
- Efficient rule evaluation
- Minimal impact on transaction processing
- Scalable WebSocket architecture