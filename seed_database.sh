#!/bin/bash

# POS System Database Seeding Script
# This script seeds the database with sample data for testing

echo "🌱 Starting POS System Database Seeding"
echo "======================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the pos-system root directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not activated"
    echo "   Run: source venv/bin/activate"
    exit 1
fi

echo "📊 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "👥 Seeding employees..."
python manage.py seed_employees

echo ""
echo "🏪 Seeding products..."
python manage.py seed_products

echo ""
echo "🔌 Initializing plugins..."
python manage.py init_plugins

echo ""
echo "✅ Database seeding completed successfully!"
echo ""
echo "📋 Seeded Data Summary:"
echo "======================="
echo "👥 Employees: john/password123, jane/password123, admin/admin123"
echo "🏪 Products: 19 items including age-restricted (beer, wine, cigarettes)"
echo "🔌 Plugins: All 5 plugins initialized and configured"
echo ""
echo "🚀 Ready to start the application!"
echo "   1. Terminal 1: daphne config.asgi:application"
echo "   2. Terminal 2: python manage.py consume_events"
echo "   3. Terminal 3: cd frontend && ./start.sh"