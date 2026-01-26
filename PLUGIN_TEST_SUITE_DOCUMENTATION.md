# POS System Plugin Test Suite Documentation

## Overview

This document provides comprehensive documentation for the POS System plugin test suite, covering all test scenarios, setup instructions, and execution guidelines for the event-driven plugin architecture.

## Test Suite Summary

**Total Test Cases: 38**
- **Employee Time Tracker**: 6 tests
- **Customer Lookup**: 6 tests  
- **Purchase Recommender**: 7 tests
- **Fraud Detection**: 8 tests
- **Age Verification**: 11 tests

## Architecture & Testing Approach

### **Testing Framework**
- **Django TestCase**: Industry standard, zero configuration
- **Database Isolation**: Each test runs in isolated transaction
- **Mock Dependencies**: All external services (Kafka, APIs, WebSockets) mocked
- **Automatic Cleanup**: Test database created/destroyed automatically

### **Plugin Architecture**
```
Frontend (GraphQL) → Django Backend → Kafka → Plugin Registry → Individual Plugins
                                        ↓
                              Event-Driven Plugin System
```

## Plugin Test Coverage

### 1. Employee Time Tracker Plugin (6 tests)

**Purpose**: Tracks employee work hours through login/logout events

**Test Scenarios:**
- ✅ **Plugin Activation**: Processes events when enabled, ignores when disabled
- ✅ **Login Tracking**: Creates time entry on employee login
- ✅ **Logout Tracking**: Completes time entry and calculates hours on logout
- ✅ **Time Calculation**: Accurate hour calculation (7.5 hours = 7.50)
- ✅ **Session Termination**: Handles forced session termination
- ✅ **Complete Workflow**: Full login→logout session flow

**Events Handled**: `EMPLOYEE_LOGIN`, `EMPLOYEE_LOGOUT`, `SESSION_TERMINATED`

**Key Features Tested:**
- Time entry creation and completion
- Decimal precision in hour calculations
- Session state management
- Event publishing to Kafka

### 2. Customer Lookup Plugin (6 tests)

**Purpose**: Fetches customer data from external API with caching

**Test Scenarios:**
- ✅ **Plugin Activation**: Processes events when enabled, ignores when disabled
- ✅ **Cache Hit**: Skips API call when fresh cache available
- ✅ **API Integration**: Creates customers from external API responses
- ✅ **Cache Fallback**: Falls back to stale cache on API failure
- ✅ **Error Handling**: Proper logging and status tracking
- ✅ **Complete Workflow**: Full basket→customer lookup→event publishing

**Events Handled**: `basket.started`

**Key Features Tested:**
- External API integration with retry logic
- TTL-based caching strategy
- Fallback mechanisms on API errors
- Customer data persistence
- Audit logging with timing metrics

### 3. Purchase Recommender Plugin (7 tests)

**Purpose**: Recommends additional items based on basket contents

**Test Scenarios:**
- ✅ **Plugin Activation**: Processes events when enabled, ignores when disabled
- ✅ **Hardcoded Rules**: Creates recommendations from built-in product rules
- ✅ **Database Rules**: Database rules override hardcoded rules
- ✅ **Unknown Products**: No recommendations for products without rules
- ✅ **WebSocket Integration**: Real-time messages sent to frontend
- ✅ **Event Publishing**: Kafka events for downstream processing
- ✅ **Complete Workflow**: Item addition→recommendation→notification

**Events Handled**: `item.added`

**Key Features Tested:**
- Hardcoded recommendation fallback rules
- Database-driven recommendation rules
- Real-time WebSocket notifications
- Multi-channel output (DB, Kafka, WebSocket)
- Priority system for rule evaluation

### 4. Fraud Detection Plugin (8 tests)

**Purpose**: Detects fraudulent activities in POS transactions

**Test Scenarios:**
- ✅ **Plugin Activation**: Processes events when enabled, ignores when disabled
- ✅ **Multiple Terminals**: Detects employee accessing multiple terminals
- ✅ **Rapid Items**: Detects items being added too quickly
- ✅ **High Value Payments**: Detects large payments in short sessions
- ✅ **Rule Management**: No alerts when rules disabled
- ✅ **State Management**: Proper tracking of sessions, terminals, baskets
- ✅ **Anonymous Payments**: Detects high-value payments without customer ID
- ✅ **Complete Workflow**: Full fraud detection with all components

**Events Handled**: `EMPLOYEE_LOGIN`, `EMPLOYEE_LOGOUT`, `SESSION_TERMINATED`, `BASKET_STARTED`, `item.added`, `CUSTOMER_IDENTIFIED`, `PAYMENT_COMPLETED`

**Key Features Tested:**
- Multi-event fraud rule engine
- In-memory state management across requests
- Real-time alert system with WebSocket notifications
- Configurable fraud rules with thresholds
- Alert severity classification (LOW/MEDIUM/HIGH/CRITICAL)

### 5. Age Verification Plugin (11 tests)

**Purpose**: Enforces age verification for restricted products

**Test Scenarios:**
- ✅ **Plugin Activation**: Processes events when enabled, ignores when disabled
- ✅ **State Management**: Basket state creation and cleanup
- ✅ **Age Restriction Detection**: Restricted items trigger verification
- ✅ **Non-Restricted Items**: No verification for regular products
- ✅ **Age Verification Success**: Customer meets age requirement
- ✅ **Age Verification Failure**: Customer doesn't meet age requirement
- ✅ **Payment Protection**: Payment blocked without verification
- ✅ **Violation Tracking**: Compliance violations recorded
- ✅ **Item Integration**: Verified items added to basket
- ✅ **State Cleanup**: Payment completion clears state
- ✅ **Complete Workflow**: Full age verification with multiple items

**Events Handled**: `basket.started`, `item.added`, `item.removed`, `age.verified`, `age.verification.cancelled`, `age.verification.completed`, `payment.initiated`, `payment.completed`

**Key Features Tested:**
- Product-based age restrictions (18+, 21+)
- Database-persisted verification state
- Payment blocking for compliance
- Violation tracking for audit trails
- Multi-item verification workflows

## Setup Instructions

### Prerequisites
```bash
# Ensure you're in the project root
cd pos-system

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### Database Setup
```bash
# Run migrations (creates test database automatically)
python manage.py makemigrations
python manage.py migrate
```

## Running Tests

### Individual Plugin Tests
```bash
# Employee Time Tracker
python manage.py test plugins.employee_time_tracker

# Customer Lookup  
python manage.py test plugins.customer_lookup

# Purchase Recommender
python manage.py test plugins.purchase_recommender

# Fraud Detection
python manage.py test plugins.fraud_detection

# Age Verification
python manage.py test plugins.age_verification
```

### All Plugin Tests
```bash
# Run all plugin tests at once
python manage.py test plugins.employee_time_tracker plugins.customer_lookup plugins.purchase_recommender plugins.fraud_detection plugins.age_verification
```

### Using Test Runner Script
```bash
# Make script executable
chmod +x run_plugin_tests.sh

# Run all plugins
./run_plugin_tests.sh all

# Run specific plugin
./run_plugin_tests.sh employee_time_tracker
./run_plugin_tests.sh customer_lookup
./run_plugin_tests.sh purchase_recommender
./run_plugin_tests.sh fraud_detection
./run_plugin_tests.sh age_verification

# Run with verbose output
./run_plugin_tests.sh all -v
./run_plugin_tests.sh fraud_detection -v
```

### Specific Test Methods
```bash
# Run individual test method
python manage.py test plugins.fraud_detection.tests.FraudDetectionPluginTest.test_multiple_terminals_fraud_detection

# Run with verbose output
python manage.py test plugins.age_verification --verbosity=2
```

## Expected Test Results

### Successful Test Run
```bash
$ ./run_plugin_tests.sh all

Running tests for all plugins...

Found 38 test(s).
System check identified no issues (0 silenced).
......................................

----------------------------------------------------------------------
Ran 38 tests in 15.802s

OK
Destroying test database for alias 'default'...
```

### Individual Plugin Results
```bash
# Employee Time Tracker: 6 tests in ~2.6s
# Customer Lookup: 6 tests in ~2.4s  
# Purchase Recommender: 7 tests in ~3.1s
# Fraud Detection: 8 tests in ~3.8s
# Age Verification: 11 tests in ~4.5s
```

## Test Database Behavior

### Automatic Management
- **Creation**: Django creates isolated test database automatically
- **Migration**: All migrations applied to test database
- **Isolation**: Each test method runs in separate transaction
- **Rollback**: Transaction rolled back after each test
- **Cleanup**: Test database destroyed after test run
- **SQLite Override**: Uses in-memory SQLite regardless of production DB

### Data Isolation
```python
class MyPluginTest(TestCase):
    def setUp(self):
        # Run before each test method
        # Creates fresh test data
        pass
    
    def test_something(self):
        # Test runs in isolated transaction
        # Database changes are rolled back after test
        pass
```

## Mock Strategy

### External Dependencies Mocked
- **Kafka Events**: `event_producer.publish()` mocked in all tests
- **External APIs**: HTTP clients mocked with controlled responses
- **WebSocket Messages**: `async_to_sync` and channel layers mocked
- **Time-based Operations**: Fixed timestamps for consistent testing

### Mock Examples
```python
# Kafka Event Mocking
@patch('plugins.customer_lookup.plugin.event_producer')
def test_something(self, mock_producer):
    # Test logic
    mock_producer.publish.assert_called_once()

# API Client Mocking
@patch('plugins.customer_lookup.plugin.CustomerAPIClient')
def test_api_call(self, mock_api_client):
    mock_client_instance = Mock()
    mock_client_instance.fetch_customer.return_value = api_data
    mock_api_client.return_value = mock_client_instance

# WebSocket Mocking
@patch('asgiref.sync.async_to_sync')
def test_websocket(self, mock_async):
    mock_group_send = Mock()
    mock_async.return_value = mock_group_send
```

## Test File Structure

```
plugins/
├── employee_time_tracker/
│   ├── tests.py                    # 6 test methods
│   └── README_TESTS.md            # Plugin-specific documentation
├── customer_lookup/
│   ├── tests.py                    # 6 test methods
│   └── README_TESTS.md            # Plugin-specific documentation
├── purchase_recommender/
│   ├── tests.py                    # 7 test methods
│   └── README_TESTS.md            # Plugin-specific documentation
├── fraud_detection/
│   ├── tests.py                    # 8 test methods
│   └── README_TESTS.md            # Plugin-specific documentation
├── age_verification/
│   ├── tests.py                    # 11 test methods
│   └── README_TESTS.md            # Plugin-specific documentation
└── run_plugin_tests.sh            # Test runner script
```

## Common Test Patterns

### Plugin Activation Testing
```python
def test_plugin_processes_events_when_enabled(self):
    """Test plugin processes events when enabled"""
    supported_events = self.plugin.get_supported_events()
    self.assertIn('expected_event', supported_events)

def test_plugin_ignores_events_when_disabled(self):
    """Test plugin ignores events when disabled via registry"""
    self.plugin_config.enabled = False
    self.plugin_config.save()
    
    from plugins.registry import plugin_registry
    enabled_plugins = plugin_registry.get_enabled_plugins()
    plugin_names = [p.name for p in enabled_plugins]
    self.assertNotIn('plugin_name', plugin_names)
```

### Event Handling Testing
```python
@patch('plugins.my_plugin.plugin.event_producer')
def test_event_handling(self, mock_producer):
    """Test complete event handling workflow"""
    # Arrange
    event_data = {'key': 'value'}
    
    # Act
    self.plugin.handle_event('event_type', event_data)
    
    # Assert
    mock_producer.publish.assert_called_once()
    published_data = mock_producer.publish.call_args[0][1]
    self.assertEqual(published_data['event_type'], 'expected_event')
```

## Troubleshooting

### Common Issues

**1. Database Migration Errors**
```bash
# Solution: Run migrations
python manage.py makemigrations
python manage.py migrate
```

**2. Import Errors**
```bash
# Solution: Ensure you're in project root and virtual environment is activated
cd pos-system
source venv/bin/activate
```

**3. Mock Assertion Failures**
```bash
# Solution: Check mock patch paths match actual import paths
# Correct: @patch('plugins.my_plugin.plugin.event_producer')
# Wrong: @patch('events.producer.event_producer')
```

**4. Test Database Issues**
```bash
# Solution: Django handles test database automatically
# No manual database setup required
```

### Debug Mode
```bash
# Run with maximum verbosity
python manage.py test plugins.fraud_detection --verbosity=2

# Run specific failing test
python manage.py test plugins.age_verification.tests.AgeVerificationPluginTest.test_age_verification_success
```

## Performance Metrics

### Test Execution Times
- **Individual Plugin**: 2-5 seconds
- **All Plugins**: ~16 seconds
- **Database Operations**: In-memory SQLite (fast)
- **Mock Overhead**: Minimal impact

### Resource Usage
- **Memory**: Low (in-memory database)
- **CPU**: Minimal (no external calls)
- **Network**: None (all mocked)
- **Disk**: Temporary test database only

## Best Practices

### Writing New Plugin Tests
1. **Follow Existing Patterns**: Use established test structure
2. **Mock External Dependencies**: Always mock Kafka, APIs, WebSockets
3. **Test Plugin Activation**: Include enabled/disabled scenarios
4. **Cover Complete Workflows**: Test end-to-end functionality
5. **Use Descriptive Names**: Clear test method names and docstrings
6. **Clean State**: Clear any persistent state in setUp()

### Test Maintenance
1. **Keep Tests Independent**: No dependencies between test methods
2. **Update Mocks**: When plugin interfaces change, update mocks
3. **Document Changes**: Update README files when adding tests
4. **Performance Monitoring**: Watch for test execution time increases

## Conclusion

This comprehensive test suite provides 38 test cases covering all critical functionality of the POS system's event-driven plugin architecture. The tests ensure reliability, maintainability, and proper isolation while providing fast feedback during development.

The test suite validates:
- ✅ Plugin activation and deactivation
- ✅ Event handling and processing
- ✅ Data persistence and retrieval
- ✅ External service integration
- ✅ Real-time communication
- ✅ Error handling and edge cases
- ✅ Complete business workflows

All tests run in complete isolation without external dependencies, ensuring consistent and reliable test execution across different environments.