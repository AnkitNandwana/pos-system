# Quick Setup Commands

## 1. Install Dependencies
pip install -r requirements.txt

## 2. Run Migrations
python manage.py makemigrations
python manage.py migrate

## 3. Create Test Employees
python manage.py create_test_employees

## 4. Create Superuser (for admin access)
python manage.py createsuperuser

## 5. Enable Plugin
# Go to http://localhost:8000/admin
# Add PluginConfiguration:
#   - Name: employee_time_tracker
#   - Enabled: True

## 6. Start Services

# Terminal 1 - Django Server
python manage.py runserver

# Terminal 2 - Kafka Consumer
python manage.py consume_events

## 7. Test GraphQL API
# Open: http://localhost:8000/graphql/

# Login Test
mutation {
  login(username: "john", password: "password123") {
    token
    employee {
      id
      username
      firstName
      lastName
      role
    }
    terminal {
      terminalId
      loginTime
      isActive
    }
  }
}

# Logout Test (use terminalId from login response)
mutation {
  logout(terminalId: "your-terminal-id-here") {
    success
    message
  }
}

# Query Time Entries
query {
  myTimeEntries(employeeId: 1) {
    id
    clockIn
    clockOut
    totalHours
    terminalId
  }
}

## Test Credentials
# john / password123 (CASHIER)
# jane / password123 (MANAGER)
# admin / admin123 (ADMIN)
