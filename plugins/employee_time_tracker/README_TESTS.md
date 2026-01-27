# Employee Time Tracker Plugin Tests

## Overview
Happy path test cases for the Employee Time Tracker plugin using **Django TestCase**.

## Test Database Behavior
- **Automatic Creation**: Django creates test database automatically
- **Isolation**: Each test runs in a transaction that's rolled back after completion
- **Fresh State**: Database is clean for each test method
- **Auto Cleanup**: Test database is destroyed when tests complete
- **SQLite Override**: Uses SQLite for tests regardless of production database

## Test Structure
```
plugins/employee_time_tracker/
└── tests.py                    # Main test file
    ├── test_plugin_processes_events_when_enabled
    ├── test_plugin_ignores_events_when_disabled
    ├── test_login_creates_time_entry
    ├── test_logout_completes_time_entry
    ├── test_accurate_time_calculation
    └── test_complete_session_workflow
```

## Running Tests

### Run All Plugin Tests
```bash
python manage.py test plugins.employee_time_tracker
```

### Run Specific Test Method
```bash
python manage.py test plugins.employee_time_tracker.tests.EmployeeTimeTrackerPluginTest.test_login_creates_time_entry
```

### Run with Verbose Output
```bash
python manage.py test plugins.employee_time_tracker --verbosity=2
```

### Using Test Runner Script
```bash
# All plugin tests
./run_plugin_tests.sh

# Specific plugin
./run_plugin_tests.sh employee_time_tracker

# With verbose output
./run_plugin_tests.sh employee_time_tracker -v
```

## Validation

### Database Verification
Tests automatically verify database state. Django TestCase handles test database isolation:

```python
class MyTest(TestCase):
    def test_something(self):
        # Each test starts with clean database
        # Test creates data, verifies results
        # Django rolls back transaction after test
        pass
```

### Plugin Configuration Setup
```python
class MyTest(TestCase):
    def setUp(self):
        self.plugin_config = PluginConfiguration.objects.create(
            name='employee_time_tracker',
            enabled=True
        )
```

## Test Coverage

### ✅ Plugin Activation
- Plugin processes events when enabled
- Plugin ignores events when disabled

### ✅ Employee Login
- Login creates time entry with correct data

### ✅ Employee Logout  
- Logout completes time entry and calculates hours

### ✅ Time Calculation
- Accurate time calculation (7.5 hours = 7.50)

### ✅ Full Workflow
- Complete login→logout session flow

## Expected Output
```bash
$ python manage.py test plugins.employee_time_tracker --verbosity=2

Creating test database for alias 'default'...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, plugins, sessions
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
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
test_accurate_time_calculation (plugins.employee_time_tracker.tests.EmployeeTimeTrackerPluginTest) ... ok
test_complete_session_workflow (plugins.employee_time_tracker.tests.EmployeeTimeTrackerPluginTest) ... ok
test_login_creates_time_entry (plugins.employee_time_tracker.tests.EmployeeTimeTrackerPluginTest) ... ok
test_logout_completes_time_entry (plugins.employee_time_tracker.tests.EmployeeTimeTrackerPluginTest) ... ok
test_plugin_ignores_events_when_disabled (plugins.employee_time_tracker.tests.EmployeeTimeTrackerPluginTest) ... ok
test_plugin_processes_events_when_enabled (plugins.employee_time_tracker.tests.EmployeeTimeTrackerPluginTest) ... ok

----------------------------------------------------------------------
Ran 6 tests in 2.634s

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
        self.plugin_config = PluginConfiguration.objects.create(...)
    
    def test_something(self):
        # Test logic using self.employee
        pass
    
    def tearDown(self):
        # Optional cleanup (usually not needed)
        pass
```

## Django TestCase Advantages

### ✅ **Benefits:**
- **Zero Configuration**: Works out of the box
- **Reliable**: Industry standard, battle-tested
- **Database Isolation**: Perfect transaction handling
- **Django Integration**: Full access to Django features
- **Simple**: Easy to understand and maintain

### ✅ **Testing Multiple Scenarios:**
```python
class TimeCalculationTest(TestCase):
    def test_various_time_calculations(self):
        test_cases = [
            (8, Decimal('8.00')),
            (7.5, Decimal('7.50')),
            (4.25, Decimal('4.25')),
        ]
        
        for hours, expected in test_cases:
            with self.subTest(hours=hours):
                # Test logic
                self.assertEqual(result, expected)
```

## Adding More Tests
Follow the Django TestCase pattern:

```python
class MyPluginTest(TestCase):
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