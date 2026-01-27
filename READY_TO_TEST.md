# ✅ KAFKA IS READY! Quick Test Guide

## Current Status
✅ Kafka running on localhost:9092
✅ Topic 'pos-events' created
✅ Database migrated
✅ Test employees created (john, jane)
✅ Plugin enabled

## Start Testing Now!

### Terminal 1: Start Django Server
```bash
cd /home/ankit/projects/personal/pos-system/backend
python manage.py runserver
```

### Terminal 2: Start Kafka Consumer
```bash
cd /home/ankit/projects/personal/pos-system/backend
python manage.py consume_events
```

### Browser: Test GraphQL API
Open: **http://localhost:8000/graphql/**

---

## Test 1: Login (Watch Terminal 2!)

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

**Expected in Terminal 2:**
```
Kafka consumer started...
Received event: EMPLOYEE_LOGIN
Plugin employee_time_tracker handled event EMPLOYEE_LOGIN
```

---

## Test 2: Auto-Logout (Login Again)

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

**Expected in Terminal 2:**
```
Received event: SESSION_TERMINATED
Plugin employee_time_tracker handled event SESSION_TERMINATED
Received event: EMPLOYEE_LOGIN
Plugin employee_time_tracker handled event EMPLOYEE_LOGIN
```

---

## Test 3: Check Time Entries

```graphql
query {
  myTimeEntries(employeeId: 1) {
    id
    clockIn
    clockOut
    totalHours
    terminalId
    employee {
      username
      firstName
    }
  }
}
```

---

## Test 4: Logout

Copy terminalId from login response, then:

```graphql
mutation {
  logout(terminalId: "paste-terminal-id-here") {
    success
    message
  }
}
```

**Expected in Terminal 2:**
```
Received event: EMPLOYEE_LOGOUT
Plugin employee_time_tracker handled event EMPLOYEE_LOGOUT
```

---

## Test 5: Verify Hours Calculated

```graphql
query {
  myTimeEntries(employeeId: 1) {
    id
    clockIn
    clockOut
    totalHours
  }
}
```

You should see totalHours calculated!

---

## Debug: View Kafka Messages Directly

```bash
docker exec broker /opt/kafka/bin/kafka-console-consumer.sh --topic pos-events --bootstrap-server localhost:9092 --from-beginning
```

---

## Test Credentials
- john / password123 (CASHIER)
- jane / password123 (MANAGER)

---

## Useful Commands

```bash
# Check Kafka status
docker ps

# View Kafka logs
docker logs broker -f

# List topics
docker exec broker /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Stop Kafka
docker-compose down

# Restart Kafka
docker-compose restart
```

---

## Django Admin
http://localhost:8000/admin

Create superuser if needed:
```bash
python manage.py createsuperuser
```

Check:
- Terminals (active sessions)
- Time entries (work hours)
- Plugin configurations (enabled plugins)
