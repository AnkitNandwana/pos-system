# 👤 Customer Lookup Plugin - Testing Guide

## ✅ Setup Complete!

- Customers app created
- Customer Lookup plugin created
- Mock API endpoint created
- Plugin registered in Kafka consumer
- GraphQL mutations and queries added
- Ready for testing!

---

## 🚀 Start Testing

### Terminal 1: Start Django Server
```bash
cd /home/ankit/projects/personal/pos-system
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Terminal 2: Start Kafka Consumer
```bash
cd /home/ankit/projects/personal/pos-system
python manage.py consume_events
```

### Terminal 3: Enable Plugin
```bash
cd /home/ankit/projects/personal/pos-system
python manage.py shell -c "from plugins.models import PluginConfiguration; PluginConfiguration.objects.get_or_create(name='customer_lookup', defaults={'enabled': True, 'description': 'Fetches customer data from external system', 'config': {'api_endpoint': 'http://localhost:8000/api/mock-customer-lookup/', 'timeout_seconds': 5, 'retry_attempts': 2, 'cache_ttl_seconds': 3600, 'fallback_to_cache_on_error': True}}); print('✅ Plugin enabled!')"
```

### Browser: GraphQL API
Open: **http://localhost:8000/graphql/**

---

## 📝 Complete Test Flow

### Test 1: Login Employee

```graphql
mutation {
  login(username: "john", password: "password123") {
    token
    employee {
      id
      username
    }
    terminal {
      terminalId
    }
  }
}
```

**Copy the `terminalId`**

---

### Test 2: Start Basket

```graphql
mutation {
  startBasket(employeeId: 1, terminalId: "YOUR_TERMINAL_ID") {
    id
    basketId
    status
  }
}
```

**Copy the `basketId`**

---

### Test 3: Identify Customer (Triggers Plugin!)

```graphql
mutation {
  identifyCustomer(
    basketId: "YOUR_BASKET_ID"
    customerIdentifier: "+1234567890"
  ) {
    success
    message
    basketId
  }
}
```

**Expected in Terminal 2:**
```
Event: CUSTOMER_IDENTIFIED
[CUSTOMER LOOKUP] Processing identifier: +1234567890 for basket: basket_xxxxx
[CUSTOMER LOOKUP] Cache miss, calling external API
[API CLIENT] Calling http://localhost:8000/api/mock-customer-lookup/+1234567890/ (attempt 1/2)
[API CLIENT] Customer found: CUST_001
[CUSTOMER LOOKUP] Created customer: CUST_001
[CUSTOMER LOOKUP] Updated basket basket_xxxxx with customer CUST_001
[CUSTOMER LOOKUP] Successfully processed CUST_001

Event: CUSTOMER_DATA_FETCHED
```

---

### Test 4: Query Customer Data

```graphql
query {
  customer(customerId: "CUST_001") {
    customerId
    firstName
    lastName
    email
    phone
    loyaltyPoints
    tier
    totalPurchases
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "customer": {
      "customerId": "CUST_001",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com",
      "phone": "+1234567890",
      "loyaltyPoints": 1250,
      "tier": "GOLD",
      "totalPurchases": "5432.50"
    }
  }
}
```

---

### Test 5: Identify Same Customer Again (Cache Hit!)

```graphql
mutation {
  startBasket(employeeId: 1, terminalId: "YOUR_TERMINAL_ID") {
    basketId
  }
}

mutation {
  identifyCustomer(
    basketId: "NEW_BASKET_ID"
    customerIdentifier: "+1234567890"
  ) {
    success
    message
  }
}
```

**Expected in Terminal 2:**
```
[CUSTOMER LOOKUP] Processing identifier: +1234567890 for basket: basket_yyyyy
[CUSTOMER LOOKUP] Cache hit for +1234567890
[CUSTOMER LOOKUP] Successfully processed CUST_001
```

**Note: No API call made! Data served from cache.**

---

### Test 6: Test Different Customer Identifiers

#### By Phone Number
```graphql
mutation {
  identifyCustomer(basketId: "basket_xxx", customerIdentifier: "+0987654321") {
    success
    message
  }
}
```

#### By Email
```graphql
mutation {
  identifyCustomer(basketId: "basket_xxx", customerIdentifier: "john@example.com") {
    success
    message
  }
}
```

#### By Card Number
```graphql
mutation {
  identifyCustomer(basketId: "basket_xxx", customerIdentifier: "CARD_123456") {
    success
    message
  }
}
```

---

### Test 7: Query Customer by Identifier

```graphql
query {
  customerByIdentifier(identifier: "+1234567890") {
    customerId
    firstName
    lastName
    tier
    loyaltyPoints
  }
}
```

---

### Test 8: View All Customers

```graphql
query {
  allCustomers {
    customerId
    firstName
    lastName
    email
    tier
    loyaltyPoints
  }
}
```

---

### Test 9: Test Unknown Customer

```graphql
mutation {
  identifyCustomer(basketId: "basket_xxx", customerIdentifier: "+9999999999") {
    success
    message
  }
}
```

**Expected in Terminal 2:**
```
[CUSTOMER LOOKUP] Processing identifier: +9999999999
[API CLIENT] Customer not found: +9999999999
[CUSTOMER LOOKUP] Customer not found: +9999999999
```

---

### Test 10: View Basket with Customer

```graphql
query {
  basket(basketId: "YOUR_BASKET_ID") {
    basketId
    customerId
    status
    items {
      productName
      quantity
    }
  }
}
```

---

## 🎯 Mock Customer Data

The mock API has these pre-configured customers:

| Identifier | Customer ID | Name | Tier | Points |
|------------|-------------|------|------|--------|
| +1234567890 | CUST_001 | John Doe | GOLD | 1250 |
| +0987654321 | CUST_002 | Jane Smith | PLATINUM | 5000 |
| john@example.com | CUST_001 | John Doe | GOLD | 1250 |
| CARD_123456 | CUST_003 | Bob Wilson | SILVER | 500 |
| +5555555555 | CUST_004 | Alice Johnson | BRONZE | 250 |

---

## 🔍 Verify in Django Admin

1. Go to: **http://localhost:8000/admin**
2. Check:
   - **Customers** → See fetched customer data
   - **Customer Lookup Logs** → See all API calls with timing
   - **Baskets** → See customer_id populated
   - **Plugin Configurations** → Verify `customer_lookup` is enabled

---

## 📊 Complete Scenario: Full POS Flow

```graphql
# 1. Employee Login
mutation {
  login(username: "john", password: "password123") {
    terminal { terminalId }
  }
}

# 2. Start Basket
mutation {
  startBasket(employeeId: 1, terminalId: "term_1") {
    basketId
  }
}

# 3. Identify Customer
mutation {
  identifyCustomer(basketId: "basket_abc", customerIdentifier: "+1234567890") {
    success
    message
  }
}

# 4. Add Items
mutation {
  addItem(
    basketId: "basket_abc"
    productId: "BURGER"
    productName: "Cheeseburger"
    quantity: 1
    price: 8.99
  ) {
    id
  }
}

# 5. Check Customer Data
query {
  customer(customerId: "CUST_001") {
    firstName
    lastName
    loyaltyPoints
    tier
  }
}

# 6. View Complete Basket
query {
  basket(basketId: "basket_abc") {
    basketId
    customerId
    status
    items {
      productName
      quantity
      price
    }
  }
}

# 7. Finalize Basket
mutation {
  finalizeBasket(basketId: "basket_abc") {
    status
  }
}
```

---

## 🧪 Test Mock API Directly

### Using Browser
```
http://localhost:8000/api/mock-customer-lookup/+1234567890/
```

### Using curl
```bash
curl http://localhost:8000/api/mock-customer-lookup/+1234567890/
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "customer_id": "CUST_001",
    "identifier": "+1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "loyalty_points": 1250,
    "tier": "GOLD",
    "total_purchases": 5432.50,
    "last_purchase_date": "2024-01-10T15:30:00Z"
  }
}
```

---

## 🐛 Troubleshooting

### Plugin not triggering?
```bash
# Check plugin is enabled
python manage.py shell -c "from plugins.models import PluginConfiguration; print(PluginConfiguration.objects.filter(name='customer_lookup', enabled=True).exists())"
```

### API call failing?
- Check Django server is running (Terminal 1)
- Test mock API directly: `curl http://localhost:8000/api/mock-customer-lookup/+1234567890/`
- Check Terminal 2 for `[API CLIENT]` logs

### Customer not saved?
- Check Terminal 2 for errors
- Verify migrations ran: `python manage.py migrate`
- Check Django admin → Customers table

### Cache not working?
- Check `cache_ttl_seconds` in plugin config
- View Customer Lookup Logs in admin to see cache hits vs API calls

---

## ✅ Success Criteria

- ✅ CUSTOMER_IDENTIFIED event published
- ✅ Customer Lookup plugin receives event
- ✅ External API called successfully
- ✅ Customer data saved to database
- ✅ CUSTOMER_DATA_FETCHED event published
- ✅ Basket updated with customer_id
- ✅ Cache prevents duplicate API calls
- ✅ All lookups logged in CustomerLookupLog

---

## 📈 Performance Testing

### Test Cache Performance

```graphql
# First call - API hit
mutation { identifyCustomer(basketId: "b1", customerIdentifier: "+1234567890") { success } }

# Second call - Cache hit (should be faster)
mutation { identifyCustomer(basketId: "b2", customerIdentifier: "+1234567890") { success } }
```

Check `duration_ms` in Django Admin → Customer Lookup Logs

---

## 🎉 Next Steps

1. Test all 5 mock customers
2. Test cache expiration (wait 1 hour or change `cache_ttl_seconds`)
3. Test API failure scenarios
4. Integrate with real external API
5. Move to next plugin: **Fraud Detection**

---

## 🔧 Plugin Configuration

Default config (can be changed in Django admin):
```json
{
  "api_endpoint": "http://localhost:8000/api/mock-customer-lookup/",
  "timeout_seconds": 5,
  "retry_attempts": 2,
  "cache_ttl_seconds": 3600,
  "fallback_to_cache_on_error": true
}
```

