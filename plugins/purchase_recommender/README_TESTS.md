# Purchase Recommender Plugin Tests

## Overview
Happy path test cases for the Purchase Recommender plugin using **Django TestCase**.

## Test Database Behavior
- **Automatic Creation**: Django creates test database automatically
- **Isolation**: Each test runs in a transaction that's rolled back after completion
- **Fresh State**: Database is clean for each test method
- **Auto Cleanup**: Test database is destroyed when tests complete
- **SQLite Override**: Uses SQLite for tests regardless of production database

## Test Structure
```
plugins/purchase_recommender/
└── tests.py                    # Main test file
    ├── test_plugin_processes_events_when_enabled
    ├── test_plugin_ignores_events_when_disabled
    ├── test_hardcoded_recommendations_created
    ├── test_database_rules_override_hardcoded
    ├── test_no_recommendations_for_unknown_product
    ├── test_websocket_message_sent
    └── test_complete_recommendation_workflow
```

## Running Tests

### Run All Plugin Tests
```bash
python manage.py test plugins.purchase_recommender
```

### Run Specific Test Method
```bash
python manage.py test plugins.purchase_recommender.tests.PurchaseRecommenderPluginTest.test_hardcoded_recommendations_created
```

### Run with Verbose Output
```bash
python manage.py test plugins.purchase_recommender --verbosity=2
```

### Using Test Runner Script
```bash
# All plugin tests
./run_plugin_tests.sh purchase_recommender

# With verbose output
./run_plugin_tests.sh purchase_recommender -v
```

## Test Coverage

### ✅ Plugin Activation
- Plugin processes events when enabled
- Plugin ignores events when disabled

### ✅ Recommendation Generation
- Hardcoded recommendations created for known products
- Database rules override hardcoded rules when available
- No recommendations for unknown products

### ✅ Real-time Communication
- WebSocket messages sent to frontend
- Proper message format and content

### ✅ Full Workflow
- Complete recommendation workflow from item addition to notification

## Plugin Functionality

### **Event Handling**
- Listens for `item.added` events
- Processes product additions to baskets
- Generates contextual recommendations

### **Recommendation Logic**
- **Database Rules**: Primary source from RecommendationRule model
- **Hardcoded Fallback**: Built-in rules for common products
- **Priority System**: Database rules take precedence

### **Multi-Channel Notifications**
- **Database Storage**: Saves recommendations to Recommendation model
- **Kafka Events**: Publishes RECOMMENDATION_SUGGESTED events
- **WebSocket Messages**: Real-time frontend notifications

### **Hardcoded Rules**
```python
HARDCODED_RULES = {
    'BURGER': [
        {'product_id': 'FRIES', 'name': 'French Fries', 'price': '2.99'},
        {'product_id': 'COKE', 'name': 'Coca Cola', 'price': '1.99'}
    ],
    'COFFEE': [
        {'product_id': 'DONUT', 'name': 'Donut', 'price': '1.99'},
        {'product_id': 'MUFFIN', 'name': 'Blueberry Muffin', 'price': '2.49'}
    ],
    # ... more rules
}
```

## Expected Output
```bash
$ python manage.py test plugins.purchase_recommender --verbosity=2

Creating test database for alias 'default'...
Operations to perform:
  Synchronize unmigrated apps: channels, corsheaders, daphne, messages, staticfiles, strawberry
  Apply all migrations: admin, auth, contenttypes, plugins, products, purchase_recommender, baskets, employees
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
  Applying purchase_recommender.0001_initial... OK
  Applying purchase_recommender.0002_recommendation_reason_and_more... OK
  Applying purchase_recommender.0003_alter_recommendation_reason_and_more... OK
  Applying purchase_recommender.0004_alter_recommendation_recommended_price... OK
  Applying baskets.0001_initial... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
test_complete_recommendation_workflow (plugins.purchase_recommender.tests.PurchaseRecommenderPluginTest) ... ok
test_database_rules_override_hardcoded (plugins.purchase_recommender.tests.PurchaseRecommenderPluginTest) ... ok
test_hardcoded_recommendations_created (plugins.purchase_recommender.tests.PurchaseRecommenderPluginTest) ... ok
test_no_recommendations_for_unknown_product (plugins.purchase_recommender.tests.PurchaseRecommenderPluginTest) ... ok
test_plugin_ignores_events_when_disabled (plugins.purchase_recommender.tests.PurchaseRecommenderPluginTest) ... ok
test_plugin_processes_events_when_enabled (plugins.purchase_recommender.tests.PurchaseRecommenderPluginTest) ... ok
test_websocket_message_sent (plugins.purchase_recommender.tests.PurchaseRecommenderPluginTest) ... ok

----------------------------------------------------------------------
Ran 7 tests in 1.923s

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
        self.product = Product.objects.create(...)
    
    def test_something(self):
        # Test logic using self.product
        pass
```

## Mock Usage

### **Event Producer Mocking:**
```python
@patch('plugins.purchase_recommender.plugin.event_producer')
def test_event_publishing(self, mock_producer):
    # Test logic
    mock_producer.publish.assert_called_once()
```

### **WebSocket Mocking:**
```python
@patch('plugins.purchase_recommender.plugin.async_to_sync')
def test_websocket_message(self, mock_async):
    mock_group_send = Mock()
    mock_async.return_value = mock_group_send
    
    # Test logic
    mock_group_send.assert_called_once()
```

### **Channel Layer Mocking:**
```python
with patch('plugins.purchase_recommender.plugin.get_channel_layer', return_value=mock_channel_layer):
    # Test logic
    pass
```

## Data Models

### **Recommendation Model**
- `basket_id`: Links to specific basket
- `source_product_id`: Product that triggered recommendation
- `recommended_product_id`: Recommended product
- `recommended_price`: Price of recommended item
- `reason`: Why this was recommended
- `status`: PENDING/ACCEPTED/REJECTED

### **RecommendationRule Model**
- `source_product`: Product that triggers recommendation
- `recommended_product`: Product to recommend
- `priority`: Rule priority (lower = higher priority)
- `is_active`: Whether rule is enabled

## Adding More Tests
Follow the Django TestCase pattern:

```python
class PurchaseRecommenderPluginTest(TestCase):
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