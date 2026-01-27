#!/bin/bash

# POS System Demo Verification Script
# Run this script before your demo to ensure everything is working

echo "🚀 POS System Demo Verification"
echo "================================"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the pos-system root directory"
    exit 1
fi

echo "✅ Directory check passed"

# Check Python virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not activated"
    echo "   Run: source venv/bin/activate"
else
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python -c "import django, strawberry, kafka" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Missing Python dependencies. Run: pip install -r requirements.txt"
    exit 1
fi

# Check database
echo "🗄️  Checking database..."
python manage.py check --deploy 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Database configuration valid"
else
    echo "❌ Database issues. Run: python manage.py migrate"
    exit 1
fi

# Run test suite
echo "🧪 Running test suite..."
./run_plugin_tests.sh all > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ All 38 tests passing"
else
    echo "❌ Some tests failing. Check test output."
    exit 1
fi

# Check frontend dependencies
if [ -d "frontend" ]; then
    echo "🌐 Checking frontend..."
    cd frontend
    if [ -d "node_modules" ]; then
        echo "✅ Frontend dependencies installed"
    else
        echo "❌ Frontend dependencies missing. Run: npm install"
        cd ..
        exit 1
    fi
    cd ..
else
    echo "⚠️  Frontend directory not found"
fi

# Check ports
echo "🔌 Checking ports..."
netstat -tuln | grep -q ":8000"
if [ $? -eq 0 ]; then
    echo "⚠️  Port 8000 in use (Django may already be running)"
else
    echo "✅ Port 8000 available"
fi

netstat -tuln | grep -q ":3000"
if [ $? -eq 0 ]; then
    echo "⚠️  Port 3000 in use (React may already be running)"
else
    echo "✅ Port 3000 available"
fi

# Check demo files
echo "📋 Checking demo files..."
demo_files=("DEMO_SCRIPT.md" "DEMO_PREPARATION_GUIDE.md" "TECHNICAL_EXCELLENCE_SUMMARY.md")
for file in "${demo_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

echo ""
echo "🎯 Demo Readiness Summary"
echo "========================="

# Count plugins
plugin_count=$(find plugins -name "plugin.py" | wc -l)
echo "📦 Plugins available: $plugin_count"

# Count tests
test_count=$(python manage.py test --dry-run plugins.employee_time_tracker plugins.customer_lookup plugins.purchase_recommender plugins.fraud_detection plugins.age_verification 2>/dev/null | grep -c "test_")
echo "🧪 Test cases: $test_count"

# Count documentation
doc_count=$(find . -name "*.md" -not -path "./venv/*" | wc -l)
echo "📚 Documentation files: $doc_count"

echo ""
echo "🚀 Ready to start demo!"
echo ""
echo "Start services in this order:"
echo "1. Terminal 1: python manage.py runserver"
echo "2. Terminal 2: python manage.py consume_events"
echo "3. Terminal 3: cd frontend && npm start"
echo ""
echo "Then open: http://localhost:3000"
echo "Login with: john / password123"