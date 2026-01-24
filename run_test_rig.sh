#!/bin/bash

# POS System Test Rig Setup and Execution Script
# This script ensures all required data exists and runs the end-to-end test

set -e

echo "🔧 Setting up POS System Test Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "Please run this script from the Django project root directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "No virtual environment detected. Consider activating one."
fi

print_status "Checking database migrations..."
python manage.py migrate --check > /dev/null 2>&1 || {
    print_status "Running database migrations..."
    python manage.py migrate
}

print_status "Setting up test data..."

# Create superuser if none exists
python manage.py shell -c "
from django.contrib.auth import get_user_model
from employees.models import Employee

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating superuser...')
    Employee.objects.create_superuser(
        username='admin',
        email='admin@pos.com',
        password='admin123',
        employee_id='EMP_ADMIN_001',
        role='ADMIN'
    )
    print('✓ Superuser created: admin/admin123')
else:
    print('✓ Superuser already exists')
"

# Create test employee if none exists
python manage.py shell -c "
from employees.models import Employee

if not Employee.objects.filter(role='CASHIER', is_active=True).exists():
    print('Creating test cashier...')
    Employee.objects.create_user(
        username='cashier1',
        email='cashier1@pos.com',
        password='cashier123',
        employee_id='EMP_CASHIER_001',
        role='CASHIER',
        first_name='John',
        last_name='Doe'
    )
    print('✓ Test cashier created: cashier1/cashier123')
else:
    print('✓ Test cashier already exists')
"

# Seed products if none exist
python manage.py shell -c "
from products.models import Product

if Product.objects.count() == 0:
    print('Creating test products...')
    
    # Regular products
    Product.objects.create(
        product_id='PROD_001',
        name='Coca Cola 500ml',
        price=2.50,
        category='Beverages'
    )
    Product.objects.create(
        product_id='PROD_002', 
        name='Snickers Bar',
        price=1.25,
        category='Candy'
    )
    Product.objects.create(
        product_id='PROD_003',
        name='Bread Loaf',
        price=3.00,
        category='Bakery'
    )
    
    # Age-restricted products
    Product.objects.create(
        product_id='PROD_BEER_001',
        name='Budweiser Beer 6-pack',
        price=8.99,
        category='Alcohol',
        age_restricted=True,
        minimum_age=21,
        age_restriction_category='alcohol'
    )
    Product.objects.create(
        product_id='PROD_CIG_001',
        name='Marlboro Cigarettes',
        price=12.50,
        category='Tobacco',
        age_restricted=True,
        minimum_age=18,
        age_restriction_category='tobacco'
    )
    
    print('✓ Test products created')
else:
    print('✓ Test products already exist')
"

# Create test customer if none exists
python manage.py shell -c "
from customers.models import Customer

if not Customer.objects.exists():
    print('Creating test customer...')
    Customer.objects.create(
        customer_id='CUST_001',
        identifier='loyalty_12345',
        first_name='Jane',
        last_name='Smith',
        email='jane.smith@email.com',
        phone='555-0123',
        loyalty_points=150,
        tier='SILVER',
        total_purchases=250.00
    )
    print('✓ Test customer created')
else:
    print('✓ Test customer already exists')
"

# Setup plugin configurations
python manage.py shell -c "
from plugins.models import PluginConfiguration

plugins = [
    ('employee_time_tracker', 'Tracks employee work hours'),
    ('purchase_recommender', 'Recommends products based on basket'),
    ('customer_lookup', 'Looks up customer information'),
    ('fraud_detection', 'Detects fraudulent activities'),
    ('age_verification', 'Verifies age for restricted products')
]

for name, description in plugins:
    config, created = PluginConfiguration.objects.get_or_create(
        name=name,
        defaults={
            'enabled': True,
            'description': description,
            'config': {}
        }
    )
    if created:
        print(f'✓ Created plugin config: {name}')
    else:
        if not config.enabled:
            config.enabled = True
            config.save()
            print(f'✓ Enabled plugin: {name}')
        else:
            print(f'✓ Plugin already configured: {name}')
"

print_success "Test environment setup complete!"

echo ""
echo "📋 Test Environment Summary:"
echo "   • Database migrations: ✓"
echo "   • Superuser: admin/admin123"
echo "   • Test cashier: cashier1/cashier123"
echo "   • Products: 5 (3 regular, 2 age-restricted)"
echo "   • Test customer: Jane Smith"
echo "   • Plugin configurations: 5 enabled"

echo ""
echo "🚀 Running End-to-End Test Rig..."
echo ""

# Run the test rig
python manage.py run_pos_test_rig --verbose --validate-plugins

echo ""
print_success "Test rig execution complete!"

echo ""
echo "📊 To view detailed results, check:"
echo "   • Django Admin: http://localhost:8000/admin"
echo "   • Time entries in employee_time_tracker app"
echo "   • Fraud alerts in fraud_detection app"
echo "   • Age verification logs in age_verification app"

echo ""
echo "🔄 To run the test again:"
echo "   python manage.py run_pos_test_rig --verbose"