# Age Verification Plugin Tests

## Overview
Happy path test cases for the Age Verification plugin using **Django TestCase**.

## Test Database Behavior
- **Automatic Creation**: Django creates test database automatically
- **Isolation**: Each test runs in a transaction that's rolled back after completion
- **Fresh State**: Database is clean for each test method
- **Auto Cleanup**: Test database is destroyed when tests complete
- **SQLite Override**: Uses SQLite for tests regardless of production database

## Test Structure
```
plugins/age_verification/
└── tests.py                    # Main test file
    ├── test_plugin_processes_events_when_enabled
    ├── test_plugin_ignores_events_when_disabled
    ├── test_basket_started_creates_state
    ├── test_age_restricted_item_triggers_verification
    ├── test_non_restricted_item_no_verification
    ├── test_age_verification_success
    ├── test_age_verification_failure
    ├── test_payment_blocked_without_verification
    ├── test_verification_completed_adds_items_to_basket
    ├── test_payment_completed_clears_state
    └── test_complete_age_verification_workflow
```

## Running Tests

### Run All Plugin Tests
```bash
python manage.py test plugins.age_verification
```

### Run Specific Test Method
```bash
python manage.py test plugins.age_verification.tests.AgeVerificationPluginTest.test_age_restricted_item_triggers_verification
```

### Run with Verbose Output
```bash
python manage.py test plugins.age_verification --verbosity=2
```

### Using Test Runner Script
```bash
# All plugin tests
./run_plugin_tests.sh age_verification

# With verbose output
./run_plugin_tests.sh age_verification -v
```

## Test Coverage

### ✅ Plugin Activation
- Plugin processes events when enabled
- Plugin ignores events when disabled

### ✅ State Management
- Basket started creates verification state
- Payment completed clears verification state

### ✅ Age Restriction Detection
- Age-restricted items trigger verification requirement
- Non-restricted items don't trigger verification

### ✅ Age Verification Process
- Successful age verification (customer meets age requirement)
- Failed age verification (insufficient customer age)
- Verification completion adds items to basket

### ✅ Payment Protection
- Payment blocked when verification required but not completed
- Violation records created for compliance tracking

### ✅ Full Workflow
- Complete age verification workflow with multiple restricted items

## Plugin Functionality

### **Event Handling**
- Listens for basket and item events:
  - `basket.started`, `item.added`, `item.removed`
  - `age.verified`, `age.verification.cancelled`, `age.verification.completed`
  - `payment.initiated`, `payment.completed`

### **Age Restriction Rules**
- **Product Categories**: Alcohol (21+), Tobacco (18+), Custom categories
- **Minimum Age Enforcement**: Configurable per product
- **Multiple Items**: Handles baskets with multiple restricted items
- **Highest Age Requirement**: Uses maximum age requirement across all items

### **Verification Process**
1. **Detection**: Age-restricted item added to basket
2. **Requirement**: Verification state created and published
3. **Verification**: Employee verifies customer age via ID check
4. **Validation**: System checks if customer meets age requirement
5. **Completion**: Verified items added to basket, state cleared

### **State Management**
- **Database Persistence**: AgeVerificationState model
- **State Manager**: Singleton for state operations
- **Basket Tracking**: Per-basket verification requirements
- **Cleanup**: Automatic state cleanup after payment

### **Compliance & Violations**
- **Violation Tracking**: AgeVerificationViolation model
- **Audit Trail**: Complete record of verification attempts
- **Payment Blocking**: Prevents sale of unverified restricted items
- **Employee Accountability**: Links violations to specific employees

## Expected Output
```bash
$ python manage.py test plugins.age_verification --verbosity=2

Creating test database for alias 'default'...
Operations to perform:
  Synchronize unmigrated apps: channels, corsheaders, daphne, messages, staticfiles, strawberry
  Apply all migrations: admin, auth, contenttypes, plugins, age_verification, products, baskets, employees
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
  Applying products.0001_initial... OK
  Applying products.0002_product_age_restricted_and_more... OK
  Applying age_verification.0001_initial... OK
  Applying baskets.0001_initial... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
test_age_restricted_item_triggers_verification (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_age_verification_failure (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_age_verification_success (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_basket_started_creates_state (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_complete_age_verification_workflow (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_non_restricted_item_no_verification (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_payment_blocked_without_verification (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_payment_completed_clears_state (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_plugin_ignores_events_when_disabled (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_plugin_processes_events_when_enabled (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok
test_verification_completed_adds_items_to_basket (plugins.age_verification.tests.AgeVerificationPluginTest) ... ok

----------------------------------------------------------------------
Ran 11 tests in 2.456s

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
        self.beer = Product.objects.create(age_restricted=True, minimum_age=21)
        # Clear any existing state
        AgeVerificationState.objects.all().delete()
    
    def test_something(self):
        # Test logic using self.beer
        pass
```

## Mock Usage

### **Event Producer Mocking:**
```python
@patch('plugins.age_verification.plugin.event_producer')
def test_event_publishing(self, mock_producer):
    # Test logic
    mock_producer.publish.assert_called_once()
```

### **State Manager Integration:**
```python
# State manager is tested through the plugin interface
state = AgeVerificationState.objects.get(basket_id='BASKET-123')
self.assertTrue(state.requires_verification)
```

## Data Models

### **AgeVerificationState Model**
- `basket_id`: Unique basket identifier
- `requires_verification`: Whether verification is needed
- `verification_completed`: Whether verification was completed
- `restricted_items`: JSON array of restricted items
- `customer_age`: Verified customer age
- `verification_method`: How age was verified (ID_CHECK, etc.)
- `verifier_employee_id`: Employee who performed verification

### **AgeVerificationViolation Model**
- `violation_id`: Unique UUID for each violation
- `basket_id`: Basket where violation occurred
- `employee`: Employee involved in violation
- `violation_type`: Type of violation (UNVERIFIED_RESTRICTED_ITEMS, etc.)
- `details`: JSON field with violation details
- `timestamp`: When violation occurred

### **Product Age Restrictions**
- `age_restricted`: Boolean flag for restricted products
- `minimum_age`: Required minimum age (18, 21, etc.)
- `age_restriction_category`: Category (ALCOHOL, TOBACCO, etc.)

## Age Verification Workflow

### **1. Item Addition**
```python
# Age-restricted item triggers verification requirement
event_data = {
    'basket_id': 'BASKET-123',
    'product_id': 'BEER001',
    'age_restricted': True,
    'minimum_age': 21
}
```

### **2. Verification Process**
```python
# Employee verifies customer age
event_data = {
    'basket_id': 'BASKET-123',
    'verifier_employee_id': employee.id,
    'customer_age': 25,
    'verification_method': 'ID_CHECK'
}
```

### **3. Payment Protection**
```python
# Payment blocked if verification incomplete
if state_manager.is_verification_required(basket_id):
    if not state_manager.is_verification_completed(basket_id):
        # Block payment, create violation
```

## Adding More Tests
Follow the Django TestCase pattern:

```python
class AgeVerificationPluginTest(TestCase):
    def setUp(self):
        # Setup test data and clear state
        AgeVerificationState.objects.all().delete()
        pass
    
    def test_new_verification_scenario(self):
        """Test description"""
        # Arrange
        # Act  
        # Assert
        pass
```