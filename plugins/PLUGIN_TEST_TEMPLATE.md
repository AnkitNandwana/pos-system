# Plugin Test Structure Template

This template provides a standardized structure for testing plugins in the POS system.

## Directory Structure
```
plugins/
├── conftest.py                    # Shared pytest fixtures
├── pytest.ini                    # Pytest configuration
└── <plugin_name>/
    ├── test_plugin.py            # Main plugin tests
    ├── conftest.py               # Plugin-specific fixtures (optional)
    └── README_TESTS.md           # Plugin test documentation
```

## Test File Template

```python
import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from freezegun import freeze_time

from employees.models import Employee
from plugins.models import PluginConfiguration
from plugins.registry import PluginRegistry
from plugins.<plugin_name>.plugin import <PluginClass>
from plugins.<plugin_name>.models import <PluginModel>


@pytest.fixture
def plugin_config():
    """Create enabled plugin configuration"""
    return PluginConfiguration.objects.create(
        name='<plugin_name>',
        enabled=True,
        description='Test configuration'
    )


@pytest.fixture
def employee():
    """Create test employee"""
    return Employee.objects.create_user(
        username='test_user',
        password='testpass123',
        employee_id='TEST001',
        role='CASHIER'
    )


@pytest.fixture
def plugin():
    """Create plugin instance"""
    return <PluginClass>()


@pytest.fixture
def registry(plugin_config):
    """Create plugin registry with registered plugin"""
    registry = PluginRegistry()
    registry.register(<PluginClass>)
    return registry


@pytest.mark.django_db
class TestPluginActivation:
    """Test plugin activation/deactivation"""
    
    def test_plugin_processes_events_when_enabled(self, registry, employee):
        """Plugin should process events when enabled"""
        # Test implementation
        pass
    
    def test_plugin_ignores_events_when_disabled(self, registry, employee, plugin_config):
        """Plugin should not process events when disabled"""
        # Test implementation
        pass


@pytest.mark.django_db
class Test<PluginName>Core:
    """Test core plugin functionality"""
    
    def test_happy_path_scenario(self, plugin, employee):
        """Test main happy path functionality"""
        # Test implementation
        pass


@pytest.mark.django_db
class Test<PluginName>Integration:
    """Test plugin integration with system"""
    
    def test_full_workflow(self, registry, employee):
        """Test complete workflow integration"""
        # Test implementation
        pass
```

## Running Tests

### Single Plugin Tests
```bash
# Run all tests for a specific plugin
pytest plugins/<plugin_name>/test_plugin.py -v

# Run specific test class
pytest plugins/<plugin_name>/test_plugin.py::TestPluginActivation -v

# Run specific test method
pytest plugins/<plugin_name>/test_plugin.py::TestPluginActivation::test_plugin_processes_events_when_enabled -v
```

### All Plugin Tests
```bash
# Run all plugin tests
pytest plugins/ -v

# Run with coverage
pytest plugins/ --cov=plugins --cov-report=html -v
```

## Test Database Behavior

### Automatic Test Database Management
- Django creates `test_<database_name>` automatically
- Each test runs in a transaction that's rolled back
- Database is fresh for each test class
- Test database is destroyed after test run

### Database Fixtures
```python
@pytest.mark.django_db  # Required for database access
def test_database_operation():
    # This test can access the database
    user = Employee.objects.create_user(username='test')
    assert user.username == 'test'
```

### Transaction Behavior
```python
@pytest.mark.django_db(transaction=True)  # For testing transactions
def test_transaction_behavior():
    # This test can test transaction behavior
    pass
```

## Best Practices

### 1. Use Fixtures for Common Setup
```python
@pytest.fixture
def sample_data():
    """Create sample data for tests"""
    return {
        'employee_id': 1,
        'terminal_id': 'TERM-001',
        'timestamp': timezone.now().isoformat()
    }
```

### 2. Use Parametrize for Multiple Test Cases
```python
@pytest.mark.parametrize("duration,expected_hours", [
    (timedelta(hours=8), Decimal('8.00')),
    (timedelta(hours=7, minutes=30), Decimal('7.50')),
])
def test_time_calculations(duration, expected_hours):
    # Test with different durations
    pass
```

### 3. Use Freeze Time for Consistent Testing
```python
def test_time_dependent_functionality():
    base_time = timezone.now()
    with freeze_time(base_time):
        # Time-dependent test logic
        pass
```

### 4. Keep Tests Focused and Simple
- One assertion per test when possible
- Clear test names that describe what's being tested
- Minimal setup required for each test

### 5. Use Descriptive Test Names
```python
def test_employee_login_creates_time_entry():
    """Clear description of what the test validates"""
    pass
```