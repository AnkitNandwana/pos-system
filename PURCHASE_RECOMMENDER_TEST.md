# 🛒 Purchase Recommender Plugin - Testing Guide

## ✅ Setup Complete!

- Products app created
- Baskets app created
- Purchase Recommender plugin created
- 15 sample products seeded
- Plugin enabled in database
- Migrations applied

---

## 🚀 Start Testing

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

### Browser: GraphQL API
Open: **http://localhost:8000/graphql/**

---

## 📝 Test Flow

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

**Copy the `terminalId` for next step**

---

### Test 2: Start a Basket

```graphql
mutation {
  startBasket(employeeId: 1, terminalId: "YOUR_TERMINAL_ID_HERE") {
    id
    basketId
    status
    createdAt
  }
}
```

**Expected in Terminal 2:**
```
Event: BASKET_STARTED
Employee ID: 1 | Terminal ID: YOUR_TERMINAL_ID
```

**Copy the `basketId` for next steps**

---

### Test 3: Add Item (Triggers Recommendation!)

```graphql
mutation {
  addItem(
    basketId: "YOUR_BASKET_ID_HERE"
    productId: "BURGER"
    productName: "Cheeseburger"
    quantity: 1
    price: 8.99
  ) {
    id
    productId
    productName
    quantity
    price
  }
}
```

**Expected in Terminal 2:**
```
Event: ITEM_ADDED
Employee ID: N/A | Terminal ID: N/A
[RECOMMENDER] Processing item: BURGER in basket: basket_xxxxx
[RECOMMENDER] Suggested 2 items for BURGER

Event: RECOMMENDATION_SUGGESTED
Employee ID: N/A | Terminal ID: N/A
```

---

### Test 4: Check Recommendations

```graphql
query {
  recommendations(basketId: "YOUR_BASKET_ID_HERE") {
    id
    sourceProductId
    recommendedProductId
    recommendedProductName
    recommendedAt
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "recommendations": [
      {
        "id": "1",
        "sourceProductId": "BURGER",
        "recommendedProductId": "FRIES",
        "recommendedProductName": "French Fries",
        "recommendedAt": "2024-01-15T10:30:00Z"
      },
      {
        "id": "2",
        "sourceProductId": "BURGER",
        "recommendedProductId": "COKE",
        "recommendedProductName": "Coca Cola",
        "recommendedAt": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

---

### Test 5: Add Another Item (Different Product)

```graphql
mutation {
  addItem(
    basketId: "YOUR_BASKET_ID_HERE"
    productId: "COFFEE"
    productName: "Coffee"
    quantity: 1
    price: 3.99
  ) {
    id
    productId
    productName
  }
}
```

**Expected in Terminal 2:**
```
[RECOMMENDER] Processing item: COFFEE in basket: basket_xxxxx
[RECOMMENDER] Suggested 2 items for COFFEE
```

---

### Test 6: View Full Basket

```graphql
query {
  basket(basketId: "YOUR_BASKET_ID_HERE") {
    basketId
    status
    items {
      productId
      productName
      quantity
      price
    }
  }
}
```

---

### Test 7: Add Item with No Recommendations

```graphql
mutation {
  addItem(
    basketId: "YOUR_BASKET_ID_HERE"
    productId: "UNKNOWN_ITEM"
    productName: "Unknown Product"
    quantity: 1
    price: 5.99
  ) {
    id
    productId
  }
}
```

**Expected in Terminal 2:**
```
[RECOMMENDER] Processing item: UNKNOWN_ITEM in basket: basket_xxxxx
[RECOMMENDER] No recommendations found for UNKNOWN_ITEM
```

---

### Test 8: Finalize Basket

```graphql
mutation {
  finalizeBasket(basketId: "YOUR_BASKET_ID_HERE") {
    basketId
    status
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "finalizeBasket": {
      "basketId": "basket_xxxxx",
      "status": "FINALIZED"
    }
  }
}
```

---

## 🎯 Hardcoded Recommendation Rules

The plugin has these built-in rules:

| Source Product | Recommended Products |
|----------------|---------------------|
| BURGER | FRIES, COKE |
| COFFEE | DONUT, MUFFIN |
| LAPTOP | MOUSE, LAPTOP_BAG |
| PHONE | PHONE_CASE, SCREEN_PROTECTOR |
| PIZZA | GARLIC_BREAD, SODA |

---

## 🔍 Verify in Django Admin

1. Go to: **http://localhost:8000/admin**
2. Check:
   - **Products** → See all 15 products
   - **Baskets** → See created baskets
   - **Basket Items** → See items added
   - **Recommendations** → See all recommendations made
   - **Plugin Configurations** → Verify `purchase_recommender` is enabled

---

## 📊 Complete Test Scenario

```graphql
# 1. Login
mutation {
  login(username: "john", password: "password123") {
    terminal { terminalId }
  }
}

# 2. Start Basket
mutation {
  startBasket(employeeId: 1, terminalId: "term_123") {
    basketId
  }
}

# 3. Add BURGER (get FRIES + COKE recommendations)
mutation {
  addItem(basketId: "basket_abc", productId: "BURGER", productName: "Cheeseburger", quantity: 1, price: 8.99) {
    id
  }
}

# 4. Accept recommendation - Add FRIES
mutation {
  addItem(basketId: "basket_abc", productId: "FRIES", productName: "French Fries", quantity: 1, price: 2.99) {
    id
  }
}

# 5. Add COFFEE (get DONUT + MUFFIN recommendations)
mutation {
  addItem(basketId: "basket_abc", productId: "COFFEE", productName: "Coffee", quantity: 1, price: 3.99) {
    id
  }
}

# 6. Check all recommendations
query {
  recommendations(basketId: "basket_abc") {
    sourceProductId
    recommendedProductId
    recommendedProductName
  }
}

# 7. View basket
query {
  basket(basketId: "basket_abc") {
    items {
      productName
      quantity
      price
    }
  }
}

# 8. Finalize
mutation {
  finalizeBasket(basketId: "basket_abc") {
    status
  }
}
```

---

## 🐛 Troubleshooting

### Plugin not triggering?
```bash
# Check plugin is enabled
python manage.py shell -c "from plugins.models import PluginConfiguration; print(PluginConfiguration.objects.filter(name='purchase_recommender', enabled=True).exists())"
```

### No recommendations showing?
- Check Terminal 2 for `[RECOMMENDER]` logs
- Verify product_id matches hardcoded rules (BURGER, COFFEE, etc.)
- Check Django admin → Recommendations table

### Kafka not receiving events?
```bash
# Check Kafka is running
docker ps

# View Kafka messages
docker exec broker /opt/kafka/bin/kafka-console-consumer.sh --topic pos-events --bootstrap-server localhost:9092 --from-beginning
```

---

## ✅ Success Criteria

- ✅ BASKET_STARTED event published
- ✅ ITEM_ADDED event published
- ✅ Purchase Recommender plugin receives event
- ✅ Recommendations saved to database
- ✅ RECOMMENDATION_SUGGESTED event published
- ✅ GraphQL query returns recommendations
- ✅ Multiple items trigger multiple recommendations

---

## 🎉 Next Steps

1. Test all 5 product categories (BURGER, COFFEE, LAPTOP, PHONE, PIZZA)
2. Add database-driven recommendation rules via Django admin
3. Implement frontend to display recommendations
4. Track recommendation acceptance rate
5. Move to next plugin: **Customer Lookup**

