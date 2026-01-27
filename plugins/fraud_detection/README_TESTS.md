# Fraud Detection Plugin Tests

## Overview
Happy path test cases for the Fraud Detection plugin using **Django TestCase**.

## Test Database Behavior
- **Automatic Creation**: Django creates test database automatically
- **Isolation**: Each test runs in a transaction that's rolled back after completion
- **Fresh State**: Database is clean for each test method
- **Auto Cleanup**: Test database is destroyed when tests complete
- **SQLite Override**: Uses SQLite for tests regardless of production database

## Test Structure
```
plugins/fraud_detection/
└── tests.py                    # Main test file
    ├── test_plugin_processes_events_when_enabled
    ├── test_plugin_ignores_events_when_disabled
    ├── test_multiple_terminals_fraud_detection
    ├── test_rapid_items_fraud_detection
    ├── test_high_value_payment_fraud_detection
    ├── test_no_alert_when_rule_disabled
    ├── test_state_manager_updates
    └── test_complete_fraud_detection_workflow
```

## Running Tests

### Run All Plugin Tests
```bash
python manage.py test plugins.fraud_detection
```

### Run Specific Test Method
```bash
python manage.py test plugins.fraud_detection.tests.FraudDetectionPluginTest.test_multiple_terminals_fraud_detection
```

### Run with Verbose Output
```bash
python manage.py test plugins.fraud_detection --verbosity=2
```

### Using Test Runner Script
```bash
# All plugin tests
./run_plugin_tests.sh fraud_detection

# With verbose output
./run_plugin_tests.sh fraud_detection -v
```

## Test Coverage

### ✅ Plugin Activation
- Plugin processes events when enabled
- Plugin ignores events when disabled

### ✅ Fraud Rule Detection
- Multiple terminal access detection
- Rapid item addition detection
- High value payment detection
- Anonymous payment detection

### ✅ State Management
- Employee session tracking
- Terminal state tracking
- Basket state tracking

### ✅ Alert System
- Fraud alert creation and storage
- Real-time WebSocket notifications
- Kafka event publishing

### ✅ Rule Management
- Rule enabling/disabling functionality
- Configurable thresholds and time windows

## Plugin Functionality

### **Event Handling**
- Listens for multiple POS events:
  - `EMPLOYEE_LOGIN`, `EMPLOYEE_LOGOUT`, `SESSION_TERMINATED`
  - `BASKET_STARTED`, `item.added`, `CUSTOMER_IDENTIFIED`
  - `PAYMENT_COMPLETED`

### **Fraud Rules**
- **Multiple Terminals**: Employee accessing multiple terminals simultaneously
- **Rapid Items**: Items being added too quickly to basket
- **High Value Payment**: Large payments in short sessions
- **Anonymous Payment**: High-value payments without customer identification
- **Rapid Checkout**: Baskets completed too quickly

### **State Management**
- **Employee Sessions**: Track login times, terminals, active baskets
- **Terminal States**: Monitor current employee, session duration
- **Basket States**: Track items, customer identification, payment amounts

### **Alert System**
- **Database Storage**: FraudAlert model with full details
- **Real-time Notifications**: WebSocket messages to affected terminals
- **Event Publishing**: Kafka events for downstream processing
- **Severity Levels**: LOW, MEDIUM, HIGH, CRITICAL

## Expected Output
```bash
$ python manage.py test plugins.fraud_detection --verbosity=2

Creating test database for alias 'default'...
Operations to perform:
  Synchronize unmigrated apps: channels, corsheaders, daphne, messages, staticfiles, strawberry
  Apply all migrations: admin, auth, contenttypes, plugins, fraud_detection, employees
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying plugins.0001_initial... OK
  Applying employees.0001_initial... OK
  Applying fraud_detection.0001_initial... OK
  Applying fraud_detection.0002_fraudalert_acknowledged... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
test_complete_fraud_detection_workflow (plugins.fraud_detection.tests.FraudDetectionPluginTest) ... ok
test_high_value_payment_fraud_detection (plugins.fraud_detection.tests.FraudDetectionPluginTest) ... ok
test_multiple_terminals_fraud_detection (plugins.fraud_detection.tests.FraudDetectionPluginTest) ... ok
test_no_alert_when_rule_disabled (plugins.fraud_detection.tests.FraudDetectionPluginTest) ... ok
test_plugin_ignores_events_when_disabled (plugins.fraud_detection.tests.FraudDetectionPluginTest) ... ok
test_plugin_processes_events_when_enabled (plugins.fraud_detection.tests.FraudDetectionPluginTest) ... ok
test_rapid_items_fraud_detection (plugins.fraud_detection.tests.FraudDetectionPluginTest) ... ok
test_state_manager_updates (plugins.fraud_detection.tests.FraudDetectionPluginTest) ... ok

----------------------------------------------------------------------
Ran 8 tests in 2.145s

OK
Destroying test database for alias 'default'...
```

## How Django TestCase Works

### **Automatic Test Database Management:**
1. **Creation**: Django creates test database automatically
2. **Migration**: Applies all migrations to test database
3. **Isolation**: Each test method runs in a transaction
4. **Rollback**: Transaction is rolled back after each test
5. **Cleanup**: Test database is destroyed after test run

### **Database Override for Tests:**
```python
# Django automatically uses SQLite for tests:
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
```

### **Django TestCase Pattern:**
```python
class MyTest(TestCase):
    def setUp(self):
        # Run before each test method
        self.employee = Employee.objects.create_user(...)
        self.fraud_rule = FraudRule.objects.create(...)
        # Clear state manager for clean tests
        state_manager.employee_sessions.clear()
    
    def test_something(self):
        # Test logic using self.employee
        pass
```

## Mock Usage

### **Event Producer Mocking:**
```python
@patch('plugins.fraud_detection.plugin.event_producer')
def test_event_publishing(self, mock_producer):
    # Test logic
    mock_producer.publish.assert_called_once()
```

### **WebSocket Mocking:**
```python
@patch('plugins.fraud_detection.plugin.async_to_sync')
def test_websocket_message(self, mock_async):
    # Test logic
    mock_async.assert_called()
```

### **Channel Layer Mocking:**
```python
with patch('plugins.fraud_detection.plugin.get_channel_layer', return_value=mock_channel_layer):
    # Test logic
    pass
```

## Data Models

### **FraudRule Model**
- `rule_id`: Unique identifier for rule type
- `name`: Human-readable rule name
- `severity`: LOW/MEDIUM/HIGH/CRITICAL
- `time_window`: Time window in seconds for rule evaluation
- `threshold`: Numeric threshold for triggering rule
- `enabled`: Whether rule is active

### **FraudAlert Model**
- `alert_id`: Unique UUID for each alert
- `rule`: Foreign key to FraudRule
- `employee`: Employee who triggered the alert
- `terminal_id`: Terminal where fraud was detected
- `basket_id`: Basket involved in fraud (if applicable)
- `severity`: Alert severity level
- `details`: JSON field with violation details
- `acknowledged`: Whether alert has been reviewed

### **State Manager**
- **Employee Sessions**: Track active terminals, login times, payments
- **Terminal States**: Monitor current employee, basket counts
- **Basket States**: Track items, customer identification, timing

## Fraud Detection Rules

### **Multiple Terminals**
```python
# Triggers when employee accesses >= 2 terminals simultaneously
threshold=2, time_window=300 (5 minutes)
```

### **Rapid Items**
```python
# Triggers when >= 5 items added within 30 seconds
threshold=5, time_window=30
```

### **High Value Payment**
```python
# Triggers when payment >= $1000 within 60 seconds of login
threshold=1000, time_window=60
```

### **Anonymous Payment**
```python
# Triggers when payment >= $500 without customer identification
threshold=500
```

## Adding More Tests
Follow the Django TestCase pattern:

```python
class FraudDetectionPluginTest(TestCase):
    def setUp(self):
        # Setup test data and clear state
        state_manager.employee_sessions.clear()
        pass
    
    def test_new_fraud_rule(self):
        """Test description"""
        # Arrange
        # Act  
        # Assert
        pass
```