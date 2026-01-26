# Event-Driven POS System with Plugin Architecture

A modern, scalable Point-of-Sale system built with event-driven architecture and dynamic plugin capabilities. Designed for retail environments requiring real-time processing, fraud detection, age verification, and customer analytics.

## 🎯 Project Overview

### Problem Statement
Traditional POS systems are monolithic, difficult to extend, and lack real-time capabilities. Retailers need flexible systems that can adapt to changing business requirements without complete rewrites.

### Solution
This POS system uses event-driven architecture with Apache Kafka as the message bus, enabling:
- **Real-time processing** of transactions and events
- **Plugin-based extensibility** for custom business logic
- **Scalable microservice-ready** architecture
- **Dynamic feature toggling** without system restarts
- **WebSocket communication** for real-time UI updates

### Key Use Cases
- **Retail Checkout**: Complete basket management with payment processing
- **Employee Management**: Time tracking and session management
- **Fraud Prevention**: Real-time transaction analysis and blocking
- **Age Verification**: Automated ID checks for restricted products
- **Customer Analytics**: Purchase history and recommendation engine

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Django Backend  │    │  Apache Kafka   │
│   (Apollo Client)│◄──►│   (GraphQL)     │◄──►│ (Docker Compose)│
│   + WebSockets  │    │   + WebSockets   │    └─────────────────┘
└─────────────────┘    └──────────────────┘              │
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   PostgreSQL     │    │  Plugin System  │
                       │   (Primary DB)   │    │                 │
                       └──────────────────┘    │ • Time Tracker  │
                                               │ • Customer Lookup│
                       ┌──────────────────┐    │ • Recommender   │
                       │      Redis       │    │ • Fraud Detection│
                       │ (WebSocket State)│    │ • Age Verification│
                       └──────────────────┘    └─────────────────┘
```

### Event Flow
1. **Frontend** sends GraphQL mutations/queries and connects via WebSockets
2. **Backend** processes requests and publishes events to Kafka
3. **Kafka** distributes events to registered consumers
4. **Plugins** consume relevant events and execute business logic
5. **WebSockets** push real-time updates to frontend
6. **Database** stores persistent state and results

## 🛠️ Technology Stack

### Frontend
- **React.js** - UI framework
- **Apollo Client** - GraphQL client
- **Material-UI** - Component library
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first CSS
- **WebSocket** - Real-time communication

### Backend
- **Django** - Web framework
- **Strawberry GraphQL** - GraphQL implementation
- **Django Channels** - WebSocket support
- **Daphne** - ASGI server for WebSocket handling
- **ASGI** - Async server gateway interface

### Event & Data Layer
- **Apache Kafka** - Event streaming platform (Docker)
- **PostgreSQL** - Primary database
- **Redis** - WebSocket channel layer

### DevOps & Testing
- **Docker Compose** - Kafka containerization
- **Django Test Framework** - Testing
- **pytest** - Advanced testing

## 📁 Project Structure

```
pos-system/
├── config/                    # Django configuration
│   ├── settings.py           # Main settings
│   ├── asgi.py              # ASGI + WebSocket config
│   └── urls.py              # URL routing
├── employees/                # Employee management
├── products/                 # Product catalog
├── baskets/                  # Shopping cart logic
├── customers/                # Customer management
├── terminals/                # POS terminal management
├── events/                   # Event handling & WebSockets
│   ├── consumer.py          # Kafka consumer
│   ├── routing.py           # WebSocket routing
│   └── session_consumer.py  # Session WebSocket handler
├── plugins/                  # Plugin implementations
│   ├── employee_time_tracker/
│   ├── customer_lookup/
│   ├── purchase_recommender/
│   ├── fraud_detection/
│   └── age_verification/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── graphql/         # GraphQL queries/mutations
│   │   ├── hooks/           # Custom React hooks
│   │   └── context/         # React context providers
│   ├── package.json
│   └── start.sh             # Frontend startup script
├── docker-compose.yml        # Kafka setup
├── manage.py                # Django management
└── requirements.txt         # Python dependencies
```

## ⚡ Core Features

### Plugin System
- **Dynamic Loading**: Plugins can be enabled/disabled via admin interface
- **Event-Driven**: Plugins subscribe to specific Kafka events
- **Isolated**: Each plugin runs independently with its own models and logic

### Event Processing
- **Real-time**: Events processed immediately via Kafka consumers
- **Reliable**: Message persistence and replay capabilities
- **Scalable**: Horizontal scaling through consumer groups

### Business Logic
- **Basket Management**: Complete shopping cart lifecycle
- **Payment Processing**: Secure transaction handling
- **Fraud Detection**: Real-time risk assessment
- **Age Verification**: Automated compliance checks
- **Employee Tracking**: Session and time management

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker & Docker Compose
- Redis 6+

### Clone Repository
```bash
git clone <repository-url>
cd pos-system
```

### Environment Setup
Create `.env` file in the root directory:
```bash
# Debug
DEBUG=True

# Database
DB_NAME=pos_db
DB_USER=pos_system_user
DB_PASSWORD=pos_system_user
DB_HOST=localhost
DB_PORT=5432

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=pos-events
```

## 📦 Installing Dependencies

### Backend Dependencies
```bash
# Create virtual environment in root directory
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
npm install
```

### Kafka Setup (Docker)
```bash
# Start Kafka using Docker Compose
docker-compose up -d

# Verify Kafka is running
docker-compose ps
```

## 🔧 Running Prerequisites

### Start Kafka Services
```bash
# Start Kafka with Docker Compose
docker-compose up -d

# Check if Kafka is running
docker-compose logs broker
```

### Create Kafka Topics
```bash
# Create pos-events topic
docker-compose exec broker kafka-topics --create --topic pos-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Verify Kafka
```bash
# List topics
docker-compose exec broker kafka-topics --list --bootstrap-server localhost:9092

# Test producer/consumer
docker-compose exec broker kafka-console-producer --topic pos-events --bootstrap-server localhost:9092
docker-compose exec broker kafka-console-consumer --topic pos-events --from-beginning --bootstrap-server localhost:9092
```

## 🗄️ Database & Seed Data

### Run Migrations
```bash
# From root directory
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Load Seed Data

#### Option 1: Run All Seeding (Recommended)
```bash
# Run comprehensive seeding script
./seed_database.sh
```

#### Option 2: Manual Seeding
```bash
# Seed employees (test users)
python manage.py seed_employees

# Seed products with age-restricted items
python manage.py seed_products

# Initialize plugins
python manage.py init_plugins
```

### Seed Data Includes
- **Employees**: Test users (john/password123, jane/password123, admin/admin123)
- **Products**: Sample inventory including age-restricted items (beer, wine, cigarettes)
- **Plugin Configs**: Pre-configured plugin settings with fraud rules

## 🏃 Running the Application

### Start Backend Services
```bash
# Terminal 1 - Django Server with WebSocket support (using Daphne)
daphne config.asgi:application

# Terminal 2 - Kafka Consumer
python manage.py consume_events
```

### Start Frontend
```bash
# Terminal 3 - React App
cd frontend
./start.sh
# OR
npm start
```

### Verify System Health
- **Backend**: http://localhost:8000/admin/
- **GraphQL Playground**: http://localhost:8000/graphql/
- **Frontend**: http://localhost:3001/ (or 3000 with npm start)
- **WebSocket**: ws://localhost:8000/ws/session/TERM001/

## 🧪 Running Test Cases

### Backend Tests
```bash
# Run all tests from root directory
python manage.py test

# Run specific plugin tests
python manage.py test plugins.employee_time_tracker
python manage.py test plugins.fraud_detection
python manage.py test plugins.age_verification
python manage.py test plugins.customer_lookup
python manage.py test plugins.purchase_recommender

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Plugin Test Script
```bash
# Run comprehensive plugin tests
./run_plugin_tests.sh all

# Run specific plugin
./run_plugin_tests.sh employee_time_tracker

# Verify demo setup
./verify_demo_setup.sh
```

### Expected Output
- **38 total test cases** across all plugins
- **100% pass rate** for core functionality
- **Coverage > 90%** for critical paths

## 🔌 API & Real-Time Communication

### GraphQL Endpoint
- **URL**: http://localhost:8000/graphql/
- **Playground**: Available in development mode
- **WebSocket**: ws://localhost:8000/graphql/ (GraphQL subscriptions)

### WebSocket Endpoints
- **Session Management**: ws://localhost:8000/ws/session/{terminal_id}/
- **Fraud Alerts**: ws://localhost:8000/ws/fraud/{terminal_id}/
- **Recommendations**: ws://localhost:8000/ws/recommendations/{terminal_id}/

### Key Mutations
```graphql
# Employee Login
mutation {
  login(username: "john", password: "password123") {
    token
    employee { id username role }
    terminal { terminalId loginTime }
  }
}

# Start Basket
mutation {
  startBasket(terminalId: "TERM001") {
    basketId
    status
  }
}

# Add Item
mutation {
  addItem(basketId: "123", productId: 1, quantity: 2) {
    success
    basketTotal
  }
}
```

### Key Queries
```graphql
# Get Employee Time Entries
query {
  myTimeEntries(employeeId: 1) {
    clockIn
    clockOut
    totalHours
  }
}

# Get Customer Purchase History
query {
  customerPurchases(customerId: "CUST001") {
    items { product quantity }
    total
    date
  }
}
```

### WebSocket Usage
```javascript
// Connect to session WebSocket
const sessionSocket = new WebSocket('ws://localhost:8000/ws/session/TERM001/');

// Listen for real-time updates
sessionSocket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle fraud alerts, recommendations, etc.
};
```

## 📊 Sample Event Flow

### Complete Transaction Example
1. **Employee Login** → `EMPLOYEE_LOGIN` event → Time tracker starts session
2. **Start Basket** → `BASKET_STARTED` event → Initialize transaction context
3. **Customer Lookup** → `CUSTOMER_IDENTIFIED` event → Load purchase history
4. **Add Item** → `ITEM_ADDED` event → Check age restrictions, fraud patterns
5. **Age Verification** → `AGE_VERIFIED` event → Compliance check passed
6. **Fraud Check** → `FRAUD_ASSESSED` event → Risk score calculated
7. **Payment** → `PAYMENT_PROCESSED` event → Transaction completed
8. **Close Basket** → `BASKET_CLOSED` event → Generate recommendations

## 🔮 Future Scope & Enhancements

### Planned Features
- **Payment Gateway Integration**: Stripe, PayPal, Square
- **Advanced ML Recommendations**: TensorFlow-based models
- **Multi-Store Support**: Centralized management
- **Mobile App**: React Native POS terminal
- **Observability**: OpenTelemetry tracing

### Technical Improvements
- **Rule Engine**: Dynamic fraud detection rules
- **Event Sourcing**: Complete audit trail
- **CQRS Pattern**: Separate read/write models
- **Kubernetes**: Container orchestration
- **Enhanced WebSocket**: More real-time features

## 🤝 Contribution & Development

### Adding New Plugins
1. Create plugin directory: `plugins/your_plugin/`
2. Implement plugin class:
```python
from plugins.base import BasePlugin

class YourPlugin(BasePlugin):
    name = "your_plugin"
    
    def get_supported_events(self):
        return ["YOUR_EVENT_TYPE"]
    
    def handle_event(self, event_type, event_data):
        # Your logic here
        pass
```
3. Add to `INSTALLED_APPS` in `config/settings.py`
4. Create migrations and run tests
5. Enable in admin interface
6. Add WebSocket routing if needed

### Coding Standards
- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: ESLint + Prettier configuration
- **Git**: Conventional commits, feature branches
- **Testing**: Minimum 80% coverage for new code

### Development Workflow
1. Fork repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Write tests first (TDD approach)
4. Implement feature
5. Run test suite: `./run_plugin_tests.sh all`
6. Submit pull request

---

## 📞 Support & Documentation

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: Detailed technical documentation
- **API Docs**: GraphQL Playground
- **Demo Guide**: DEMO_SCRIPT.md

**Built with ❤️ for modern retail experiences**