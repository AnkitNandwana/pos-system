# 🔍 Customer Lookup - Auto-Fetch on Basket Start

## ✅ Implementation Complete

### What Was Built:
1. **Modified `startBasket` mutation** - Added optional `customerIdentifier` parameter
2. **Customer Lookup Plugin** - Listens to `BASKET_STARTED` event
3. **External API Client** - Fetches customer data with retry logic
4. **Mock API** - Returns customer data for testing
5. **Event Flow** - Publishes `CUSTOMER_DATA_FETCHED` event

---

## 🚀 Quick Start

### Terminal 1: Start Django Server
```bash
python manage.py runserver
```

### Terminal 2: Start Kafka Consumer
```bash
python manage.py consume_events
```

### Browser: GraphQL
http://localhost:8000/graphql/

---

## 📝 Test Scenarios

### Test 1: Start Basket WITH Customer Identifier

```graphql
mutation {
  startBasket(
    employeeId: 1
    terminalId: "term_001"
    customerIdentifier: "+1234567890"
  ) {
    id
    basketId
    status
    customerId
    createdAt
  }
}
```

**Expected in Terminal 2:**
```
Event: BASKET_STARTED
Employee ID: 1 | Terminal ID: term_001
[CUSTOMER LOOKUP] Processing identifier: +1234567890 for basket: basket_xxxxx
[API] Fetching customer: +1234567890 (attempt 1/2)
[API] Success: CUST_001
[CUSTOMER LOOKUP] Created customer: CUST_001
[CUSTOMER LOOKUP] Updated basket basket_xxxxx with customer CUST_001
[CUSTOMER LOOKUP] Successfully processed CUST_001

Event: CUSTOMER_DATA_FETCHED
Employee ID: N/A | Terminal ID: N/A
```

---

### Test 2: Start Basket WITHOUT Customer (Guest)

```graphql
mutation {
  startBasket(
    employeeId: 1
    terminalId: "term_001"
  ) {
    basketId
    status
    customerId
  }
}
```

**Expected:**
- Basket created
- No customer lookup triggered
- `customerId` is null

---

### Test 3: Query Customer Data

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

### Test 4: Second Lookup (Cache Hit)

```graphql
mutation {
  startBasket(
    employeeId: 1
    terminalId: "term_002"
    customerIdentifier: "+1234567890"
  ) {
    basketId
    customerId
  }
}
```

**Expected in Terminal 2:**
```
[CUSTOMER LOOKUP] Processing identifier: +1234567890 for basket: basket_yyyyy
[CUSTOMER LOOKUP] Cache hit for +1234567890
[CUSTOMER LOOKUP] Updated basket basket_yyyyy with customer CUST_001
[CUSTOMER LOOKUP] Successfully processed CUST_001
```

**Note:** No API call! Data served from cache (fast).

---

### Test 5: Unknown Customer

```graphql
mutation {
  startBasket(
    employeeId: 1
    terminalId: "term_003"
    customerIdentifier: "+9999999999"
  ) {
    basketId
    customerId
  }
}
```

**Expected in Terminal 2:**
```
[CUSTOMER LOOKUP] Processing identifier: +9999999999 for basket: basket_zzzzz
[API] Fetching customer: +9999999999 (attempt 1/2)
[API] Customer not found: +9999999999
[CUSTOMER LOOKUP] Customer not found: +9999999999
```

**Response:**
- Basket created
- `customerId` is null (guest checkout)

---

## 🎯 Mock API Test Customers

| Identifier | Customer ID | Name | Tier | Points |
|------------|-------------|------|------|--------|
| +1234567890 | CUST_001 | John Doe | GOLD | 1250 |
| +0987654321 | CUST_002 | Jane Smith | PLATINUM | 5000 |
| john@example.com | CUST_001 | John Doe | GOLD | 1250 |
| CARD_123456 | CUST_003 | Bob Wilson | SILVER | 500 |
| +5555555555 | CUST_004 | Alice Johnson | BRONZE | 250 |

---

## 🔄 Complete Flow

```graphql
# 1. Login employee
mutation {
  login(username: "john", password: "password123") {
    terminal { terminalId }
  }
}

# 2. Start basket with customer
mutation {
  startBasket(
    employeeId: 1
    terminalId: "term_001"
    customerIdentifier: "+1234567890"
  ) {
    basketId
    customerId
  }
}

# 3. Add items
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

# 4. View basket with customer
query {
  basket(basketId: "basket_abc") {
    basketId
    customerId
    items {
      productName
      price
    }
  }
}

# 5. Finalize
mutation {
  finalizeBasket(basketId: "basket_abc") {
    status
  }
}
```

---

## 📊 Verify in Django Admin

http://localhost:8000/admin

Check:
1. **Customers** → See fetched customer data
2. **Customer Lookup Logs** → See API call history with timing
3. **Baskets** → See `customer_id` populated

---

## 🐛 Troubleshooting

### Plugin not triggering?
```bash
# Check plugin is enabled
python manage.py shell -c "from plugins.models import PluginConfiguration; print(PluginConfiguration.objects.filter(name='customer_lookup', enabled=True).exists())"
```

### API not responding?
```bash
# Test mock API directly
curl http://localhost:8000/api/mock-customer-lookup/+1234567890/
```

### Check logs
Look for `[CUSTOMER LOOKUP]` and `[API]` prefixes in Terminal 2

---

## ⚙️ Plugin Configuration

Update in Django Admin → Plugin Configurations → customer_lookup:

```json
{
  "api_endpoint": "http://localhost:8000/api/mock-customer-lookup/",
  "timeout_seconds": 5,
  "retry_attempts": 2,
  "cache_ttl_seconds": 3600,
  "fallback_to_cache_on_error": true
}
```

---

## ✅ Success Criteria

- ✅ Basket starts with customer identifier
- ✅ BASKET_STARTED event published with identifier
- ✅ Plugin receives event and calls external API
- ✅ Customer data saved to database
- ✅ Basket updated with customer_id
- ✅ CUSTOMER_DATA_FETCHED event published
- ✅ Subsequent lookups use cache (fast)
- ✅ All API calls logged with timing

---

## 🎉 Benefits

1. **Single Mutation** - No separate customer lookup call needed
2. **Automatic** - Customer data fetched in background
3. **Fast** - Cache reduces API calls
4. **Resilient** - Retry logic and fallback to cache
5. **Auditable** - All API calls logged
6. **Flexible** - Optional parameter, supports guest checkout

---

## 🔗 Integration Points

Other plugins can now listen to `CUSTOMER_DATA_FETCHED` event:
- **Loyalty Plugin** - Apply tier-based discounts
- **Recommendation Plugin** - Personalized product suggestions
- **Fraud Detection** - Check customer history
- **Marketing Plugin** - Track customer behavior
