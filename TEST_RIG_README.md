# POS System End-to-End Test Rig

## Overview

This test rig simulates a complete POS transaction journey using **real database data** and validates the behavior of all plugins in the event-driven system. It's designed to resemble how QA or SRE teams would validate the system before production deployment.

## Architecture Validation

The test rig validates this event flow:
```
Employee Login → Basket Started → Customer Identified → Items Added → Age Verification → Subtotal → Payment → Employee Logout
```

**Plugin Interactions Tested:**
- **Employee Time Tracker**: Session tracking and hours calculation
- **Customer Lookup**: Customer data retrieval and profile loading
- **Purchase Recommender**: Basket analysis and recommendation generation
- **Fraud Detection**: Pattern analysis and alert generation
- **Age Verification**: Restricted item validation and approval workflow

## Quick Start

### 1. Setup and Run Test Rig
```bash
# Make sure Kafka consumer is running in another terminal
python manage.py consume_events

# Run the complete test setup and execution
./run_test_rig.sh
```

### 2. Manual Execution (Alternative)
```bash
# Run just the test rig
python manage.py run_pos_test_rig --verbose --validate-plugins

# Validate results after execution
python manage.py validate_test_results --detailed
```

## Test Rig Components

### 1. Main Test Rig (`run_pos_test_rig.py`)

**Features:**
- ✅ Uses real database data (no hardcoded IDs)
- ✅ Validates preconditions before execution
- ✅ Publishes events in correct sequence with realistic timing
- ✅ Structured logging with correlation IDs
- ✅ Comprehensive error handling
- ✅ Idempotent execution (can run multiple times)

**Event Sequence:**
1. `EMPLOYEE_LOGIN` - Creates terminal session
2. `basket.started` - Initializes shopping basket
3. `customer.identified` - Links customer to basket
4. `item.added` (multiple) - Adds regular and age-restricted items
5. `age.verified` - Approves age-restricted purchase
6. `subtotal.finalized` - Calculates totals and taxes
7. `payment.completed` - Processes payment
8. `EMPLOYEE_LOGOUT` - Ends terminal session

### 2. Environment Setup (`run_test_rig.sh`)

**Automated Setup:**
- Database migrations
- Superuser creation (`admin/admin123`)
- Test employee creation (`cashier1/cashier123`)
- Product seeding (3 regular + 2 age-restricted)
- Test customer creation
- Plugin configuration validation

### 3. Result Validation (`validate_test_results.py`)

**Validation Categories:**
- **Employee Time Tracker**: Time entry creation and hours calculation
- **Fraud Detection**: Rule evaluation and alert generation
- **Age Verification**: Verification logs and approval workflow
- **Purchase Recommender**: Recommendation generation capability
- **Customer Lookup**: Customer data retrieval success
- **Data Consistency**: Cross-plugin data integrity
- **Plugin Configurations**: All plugins enabled and configured

## Command Reference

### Test Rig Execution
```bash
# Basic execution
python manage.py run_pos_test_rig

# Verbose output with plugin validation
python manage.py run_pos_test_rig --verbose --validate-plugins
```

### Result Validation
```bash
# Basic validation summary
python manage.py validate_test_results

# Detailed validation with test breakdown
python manage.py validate_test_results --detailed

# Validate specific test run
python manage.py validate_test_results --correlation-id <ID> --detailed
```

## Expected Outcomes

### Successful Test Run Should Show:
```
✅ Test rig completed successfully!
   Duration: 2.34s
   Events: 8
   Time Entries: 1
   Fraud Alerts: 0-3 (depending on rules triggered)
   Age Verifications: 1
```

### Validation Results Should Show:
```
VALIDATION SUMMARY
============================================================
Employee Time Tracker    ✓ PASS
Fraud Detection          ✓ PASS  
Age Verification         ✓ PASS
Purchase Recommender     ✓ PASS
Customer Lookup          ✓ PASS
Data Consistency         ✓ PASS
Plugin Configurations    ✓ PASS
------------------------------------------------------------
🎉 ALL VALIDATIONS PASSED (7/7)
```

## Database Verification

After running the test rig, you can verify results in Django Admin:

### Time Tracking
- **URL**: http://localhost:8000/admin/employee_time_tracker/timeentry/
- **Check**: Clock in/out times and calculated hours

### Fraud Detection
- **URL**: http://localhost:8000/admin/fraud_detection/fraudalert/
- **Check**: Generated alerts and rule violations

### Age Verification
- **URL**: http://localhost:8000/admin/age_verification/ageverificationlog/
- **Check**: Verification attempts and results

### Baskets & Items
- **URL**: http://localhost:8000/admin/baskets/basket/
- **Check**: Basket creation and item additions

## Troubleshooting

### Common Issues

**1. "No active CASHIER employee found"**
```bash
# Run setup script to create test data
./run_test_rig.sh
```

**2. "Need at least 1 age-restricted product"**
```bash
# Seed products manually
python manage.py seed_products
```

**3. "Kafka connection failed"**
```bash
# Ensure Kafka is running
docker-compose up -d kafka

# Check Kafka consumer is running
python manage.py consume_events
```

**4. Plugin not processing events**
```bash
# Check plugin configuration
python manage.py shell -c "
from plugins.models import PluginConfiguration
for p in PluginConfiguration.objects.all():
    print(f'{p.name}: {p.enabled}')
"
```

### Debug Mode

For detailed debugging, run with maximum verbosity:
```bash
python manage.py run_pos_test_rig --verbose 2>&1 | tee test_rig_debug.log
```

## Test Data Requirements

### Minimum Database State:
- ✅ 1 active CASHIER employee
- ✅ 3+ regular products
- ✅ 1+ age-restricted product
- ✅ 1+ customer record
- ✅ 1+ active terminal
- ✅ All 5 plugins configured and enabled

### Auto-Created Test Data:
- **Employee**: `cashier1` / `cashier123`
- **Customer**: Jane Smith (loyalty_12345)
- **Products**: Coca Cola, Snickers, Bread, Beer, Cigarettes
- **Terminal**: Auto-generated TEST_TERMINAL_*

## Integration with CI/CD

### GitHub Actions Example:
```yaml
- name: Run POS Test Rig
  run: |
    python manage.py consume_events &
    sleep 5
    ./run_test_rig.sh
    python manage.py validate_test_results --detailed
```

### Docker Compose Testing:
```yaml
test-rig:
  build: .
  depends_on:
    - kafka
    - postgres
  command: ./run_test_rig.sh
  environment:
    - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

## Performance Benchmarks

**Expected Performance:**
- **Test Duration**: 2-5 seconds
- **Events Published**: 8 core events + plugin-generated events
- **Database Operations**: ~50 queries
- **Memory Usage**: <100MB additional

**Scalability Testing:**
```bash
# Run multiple concurrent test rigs
for i in {1..5}; do
  python manage.py run_pos_test_rig --verbose &
done
wait
```

## Extending the Test Rig

### Adding New Event Types:
1. Add event to `run_pos_test_rig.py`
2. Update validation in `validate_test_results.py`
3. Document expected plugin behavior

### Adding New Plugins:
1. Register plugin in `consume_events.py`
2. Add validation logic in `validate_test_results.py`
3. Update precondition checks if needed

### Custom Test Scenarios:
```python
# Create custom test rig for specific scenarios
class CustomPOSTestRig(POSTestRig):
    def run_fraud_scenario(self):
        # Implement fraud-triggering sequence
        pass
```

## Success Criteria Summary

✅ **Event Ordering**: All events published in correct sequence  
✅ **Plugin Eligibility**: Only enabled plugins process events  
✅ **Stateful Behavior**: Plugins maintain state across events  
✅ **Cross-Plugin Interactions**: Customer lookup → fraud detection  
✅ **Correct Event Emissions**: Plugins publish expected secondary events  
✅ **Data Integrity**: Database state consistent across all plugins  
✅ **Error Handling**: Graceful failure with meaningful error messages  
✅ **Repeatability**: Can run multiple times without conflicts  

This test rig provides comprehensive validation of your event-driven POS system and ensures all plugins work correctly in a realistic transaction scenario.