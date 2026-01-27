# Testing Employee Login/Logout with Auto-Logout

## Setup Steps

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Test Employees
```bash
python manage.py create_test_employees
```

Or create manually via Django shell:
```bash
python manage.py shell
```
```python
from employees.models import Employee
Employee.objects.create_user(username='john', password='password123', first_name='John', last_name='Doe', employee_id='EMP001', role='CASHIER')
Employee.objects.create_user(username='jane', password='password123', first_name='Jane', last_name='Smith', employee_id='EMP002', role='MANAGER')
```

### 3. Enable Plugin in Django Admin
```bash
python manage.py createsuperuser  # If not created yet
python manage.py runserver
```

Go to http://localhost:8000/admin
- Login with superuser credentials
- Go to "Plugin configurations" → "Add Plugin Configuration"
- Name: `employee_time_tracker`
- Enabled: ✓ (checked)
- Description: "Tracks employee work hours"
- Save

### 4. Start Kafka Consumer (in separate terminal)
```bash
python manage.py consume_events
```

### 5. Start Django Server (in another terminal)
```bash
python manage.py runserver
```

---

## Testing with GraphQL API

### Access GraphQL Playground
Open: http://localhost:8000/graphql/

---

## Test Scenario 1: Simple Login

**Mutation:**
```graphql
mutation {
  login(username: "john", password: "password123") {
    token
    employee {
      id
      username
      firstName
      lastName
      role
      employeeId
    }
    terminal {
      id
      terminalId
      loginTime
      isActive
    }
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "login": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "employee": {
        "id": "1",
        "username": "john",
        "firstName": "John",
        "lastName": "Doe",
        "role": "CASHIER",
        "employeeId": "EMP001"
      },
      "terminal": {
        "id": "1",
        "terminalId": "abc-123-xyz",
        "loginTime": "2024-01-15T10:30:00",
        "isActive": true
      }
    }
  }
}
```

**What Happens:**
1. ✅ Employee authenticated
2. ✅ Terminal session created
3. ✅ JWT token generated
4. ✅ EMPLOYEE_LOGIN event published to Kafka
5. ✅ Kafka consumer receives event
6. ✅ Employee Time Tracker plugin creates TimeEntry

---

## Test Scenario 2: Auto-Logout (Login While Already Logged In)

**Step 1:** Login as John (first time)
```graphql
mutation {
  login(username: "john", password: "password123") {
    token
    terminal {
      terminalId
      isActive
    }
  }
}
```

**Step 2:** Login as John again (without logging out)
```graphql
mutation {
  login(username: "john", password: "password123") {
    token
    terminal {
      terminalId
      isActive
    }
  }
}
```

**Expected Behavior:**
1. ✅ Old terminal session terminated automatically
2. ✅ SESSION_TERMINATED event published
3. ✅ Old TimeEntry gets clock_out time and total_hours calculated
4. ✅ New terminal session created
5. ✅ EMPLOYEE_LOGIN event published
6. ✅ New TimeEntry created

**Check in Kafka Consumer Terminal:**
You should see:
```
Received event: SESSION_TERMINATED
Plugin employee_time_tracker handled event SESSION_TERMINATED
Received event: EMPLOYEE_LOGIN
Plugin employee_time_tracker handled event EMPLOYEE_LOGIN
```

---

## Test Scenario 3: Logout

**Step 1:** Login first
```graphql
mutation {
  login(username: "john", password: "password123") {
    token
    terminal {
      terminalId
    }
  }
}
```

**Step 2:** Copy the terminalId from response, then logout
```graphql
mutation {
  logout(terminalId: "paste-terminal-id-here") {
    success
    message
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "logout": {
      "success": true,
      "message": "Logged out successfully"
    }
  }
}
```

**What Happens:**
1. ✅ Terminal session marked inactive
2. ✅ Logout time recorded
3. ✅ EMPLOYEE_LOGOUT event published
4. ✅ TimeEntry updated with clock_out and total_hours

---

## Test Scenario 4: Query Time Entries

**Query:**
```graphql
query {
  myTimeEntries(employeeId: 1) {
    id
    terminalId
    clockIn
    clockOut
    totalHours
    employee {
      username
      firstName
    }
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "myTimeEntries": [
      {
        "id": "2",
        "terminalId": "xyz-456-abc",
        "clockIn": "2024-01-15T14:30:00",
        "clockOut": "2024-01-15T18:45:00",
        "totalHours": "4.25",
        "employee": {
          "username": "john",
          "firstName": "John"
        }
      },
      {
        "id": "1",
        "terminalId": "abc-123-xyz",
        "clockIn": "2024-01-15T10:00:00",
        "clockOut": "2024-01-15T14:00:00",
        "totalHours": "4.00",
        "employee": {
          "username": "john",
          "firstName": "John"
        }
      }
    ]
  }
}
```

---

## Test Scenario 5: Multiple Employees

**Login as John:**
```graphql
mutation {
  login(username: "john", password: "password123") {
    token
    terminal { terminalId }
  }
}
```

**Login as Jane (in another browser/tab):**
```graphql
mutation {
  login(username: "jane", password: "password123") {
    token
    terminal { terminalId }
  }
}
```

**Expected Behavior:**
- ✅ Both employees have separate active sessions
- ✅ Both have separate TimeEntry records
- ✅ No interference between sessions

---

## Verify in Django Admin

1. Go to http://localhost:8000/admin
2. Check **Terminals** - see active/inactive sessions
3. Check **Time entries** - see clock in/out times and total hours
4. Check **Plugin configurations** - ensure employee_time_tracker is enabled

---

## Troubleshooting

### Issue: "Invalid credentials"
- Ensure employee exists: `python manage.py create_test_employees`
- Check password is correct

### Issue: No events in Kafka consumer
- Ensure Kafka is running: `docker ps` or check Kafka service
- Check KAFKA_BOOTSTRAP_SERVERS in .env
- Restart consumer: `python manage.py consume_events`

### Issue: Plugin not working
- Check plugin is enabled in Django admin
- Check consumer terminal for errors
- Verify plugin registered in consume_events.py

### Issue: TimeEntry not created
- Check Kafka consumer is running
- Check plugin configuration is enabled
- Look for errors in consumer terminal

---

## Complete Test Flow

```bash
# Terminal 1: Start Django
python manage.py runserver

# Terminal 2: Start Kafka Consumer
python manage.py consume_events

# Browser: Open GraphQL
http://localhost:8000/graphql/

# Test 1: Login
mutation { login(username: "john", password: "password123") { token terminal { terminalId } } }

# Test 2: Login again (auto-logout test)
mutation { login(username: "john", password: "password123") { token terminal { terminalId } } }

# Test 3: Query time entries
query { myTimeEntries(employeeId: 1) { id clockIn clockOut totalHours } }

# Test 4: Logout
mutation { logout(terminalId: "your-terminal-id") { success message } }

# Test 5: Query again to see updated hours
query { myTimeEntries(employeeId: 1) { id clockIn clockOut totalHours } }
```

---

## Expected Kafka Consumer Output

```
Kafka consumer started...
Received event: EMPLOYEE_LOGIN
Plugin employee_time_tracker handled event EMPLOYEE_LOGIN
Received event: SESSION_TERMINATED
Plugin employee_time_tracker handled event SESSION_TERMINATED
Received event: EMPLOYEE_LOGIN
Plugin employee_time_tracker handled event EMPLOYEE_LOGIN
Received event: EMPLOYEE_LOGOUT
Plugin employee_time_tracker handled event EMPLOYEE_LOGOUT
```
