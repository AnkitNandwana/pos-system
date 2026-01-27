# Customer Lookup Plugin Tests

## Overview
Happy path test cases for the Customer Lookup plugin using **Django TestCase**.

## Test Database Behavior
- **Automatic Creation**: Django creates test database automatically
- **Isolation**: Each test runs in a transaction that's rolled back after completion
- **Fresh State**: Database is clean for each test method
- **Auto Cleanup**: Test database is destroyed when tests complete
- **SQLite Override**: Uses SQLite for tests regardless of production database

## Test Structure
```
plugins/customer_lookup/
└── tests.py                    # Main test file
    ├── test_plugin_processes_events_when_enabled
    ├── test_plugin_ignores_events_when_disabled
    ├── test_cache_hit_skips_api_call
    ├── test_api_call_creates_customer
    ├── test_api_failure_with_cache_fallback
    └── test_complete_lookup_workflow
```

## Running Tests

### Run All Plugin Tests
```bash
python manage.py test plugins.customer_lookup
```

### Run Specific Test Method
```bash
python manage.py test plugins.customer_lookup.tests.CustomerLookupPluginTest.test_cache_hit_skips_api_call
```

### Run with Verbose Output
```bash
python manage.py test plugins.customer_lookup --verbosity=2
```

### Using Test Runner Script
```bash
# All plugin tests
./run_plugin_tests.sh customer_lookup

# With verbose output
./run_plugin_tests.sh customer_lookup -v
```

## Test Coverage

### ✅ Plugin Activation
- Plugin processes events when enabled
- Plugin ignores events when disabled

### ✅ Cache Management
- Cache hit skips external API call
- Fresh cache data is used when available

### ✅ External API Integration
- API call creates new customer records
- Customer data is properly saved to database

### ✅ Error Handling
- API failure falls back to cache when configured
- Proper error logging and status tracking

### ✅ Full Workflow
- Complete customer lookup workflow from basket start to data fetch

## Plugin Functionality

### **Event Handling**
- Listens for `basket.started` events
- Processes customer identifier from event data
- Updates basket with customer information

### **Caching Strategy**
- Checks local cache first (Customer model)
- Uses configurable TTL (default: 3600 seconds)
- Falls back to cache on API errors

### **External API Integration**
- Fetches customer data from external system
- Configurable timeout and retry attempts
- Comprehensive error handling

### **Data Management**
- Creates/updates Customer records
- Links customers to baskets
- Publishes CUSTOMER_DATA_FETCHED events
- Logs all lookup attempts for audit trail

## Expected Output
```bash
$ python manage.py test plugins.customer_lookup --verbosity=2

Creating test database for alias 'default'...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, plugins, sessions, customers, baskets, employees
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
  Applying customers.0001_initial... OK
  Applying baskets.0001_initial... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
test_api_call_creates_customer (plugins.customer_lookup.tests.CustomerLookupPluginTest) ... ok
test_api_failure_with_cache_fallback (plugins.customer_lookup.tests.CustomerLookupPluginTest) ... ok
test_cache_hit_skips_api_call (plugins.customer_lookup.tests.CustomerLookupPluginTest) ... ok
test_complete_lookup_workflow (plugins.customer_lookup.tests.CustomerLookupPluginTest) ... ok
test_plugin_ignores_events_when_disabled (plugins.customer_lookup.tests.CustomerLookupPluginTest) ... ok
test_plugin_processes_events_when_enabled (plugins.customer_lookup.tests.CustomerLookupPluginTest) ... ok

----------------------------------------------------------------------
Ran 6 tests in 1.847s

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
        self.plugin_config = PluginConfiguration.objects.create(...)
        self.customer = Customer.objects.create(...)
    
    def test_something(self):
        # Test logic using self.customer
        pass
```

## Mock Usage

### **External API Mocking:**
```python
@patch('plugins.customer_lookup.plugin.CustomerAPIClient')
def test_api_call(self, mock_api_client):
    mock_client_instance = Mock()
    mock_client_instance.fetch_customer.return_value = api_data
    mock_api_client.return_value = mock_client_instance
    
    # Test logic
    pass
```

### **Event Producer Mocking:**
```python
@patch('plugins.customer_lookup.plugin.event_producer')
def test_event_publishing(self, mock_producer):
    # Test logic
    mock_producer.publish.assert_called_once()
```

## Adding More Tests
Follow the Django TestCase pattern:

```python
class CustomerLookupPluginTest(TestCase):
    def setUp(self):
        # Setup test data
        pass
    
    def test_new_functionality(self):
        """Test description"""
        # Arrange
        # Act  
        # Assert
        pass
```