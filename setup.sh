#!/bin/bash

echo "=========================================="
echo "POS System - Complete Setup"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop first."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker found"

# Start Kafka
echo ""
echo "Starting Kafka with Docker Compose..."
docker-compose up -d

# Wait for Kafka to be ready
echo "Waiting for Kafka to start (15 seconds)..."
sleep 15

# Create Kafka topic
echo ""
echo "Creating Kafka topic: pos-events"
docker exec -it $(docker ps -q -f name=kafka) kafka-topics --create --topic pos-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 2>/dev/null || echo "Topic already exists"

# Run migrations
echo ""
echo "Running Django migrations..."
cd backend
python manage.py makemigrations
python manage.py migrate

# Create test employees
echo ""
echo "Creating test employees..."
python manage.py create_test_employees

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Enable Plugin:"
echo "   - Create superuser: python manage.py createsuperuser"
echo "   - Start server: python manage.py runserver"
echo "   - Go to: http://localhost:8000/admin"
echo "   - Add PluginConfiguration: name='employee_time_tracker', enabled=True"
echo ""
echo "2. Start Services (in separate terminals):"
echo "   Terminal 1: python manage.py runserver"
echo "   Terminal 2: python manage.py consume_events"
echo ""
echo "3. Test GraphQL API:"
echo "   Open: http://localhost:8000/graphql/"
echo ""
echo "Test Credentials:"
echo "  john / password123 (CASHIER)"
echo "  jane / password123 (MANAGER)"
echo "  admin / admin123 (ADMIN)"
echo ""
