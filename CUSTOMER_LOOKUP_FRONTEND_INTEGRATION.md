# Customer Lookup Plugin - Frontend Integration

## Implementation Summary

### ✅ Components Created

1. **usePluginStatus Hook** (`/hooks/usePluginStatus.js`)
   - Checks if customer_lookup plugin is enabled via GraphQL
   - Returns `{ isEnabled, loading }`

2. **CustomerInput Component** (`/components/CustomerInput.jsx`)
   - Shows customer ID input field ONLY when plugin is enabled
   - Hides completely when plugin is disabled
   - Supports phone, email, card number formats

3. **PluginToggle Component** (`/components/PluginToggle.jsx`)
   - Allows cashier to enable/disable customer lookup plugin
   - Uses existing GraphQL mutations
   - Shows current plugin status

4. **BasketCreation Component** (`/components/BasketCreation.jsx`)
   - Integrates customer lookup with basket creation
   - Conditionally includes customerIdentifier in GraphQL mutation
   - Shows plugin status and customer input

5. **CustomerDisplay Component** (`/components/CustomerDisplay.jsx`)
   - Shows customer info when available
   - Displays loyalty tier, points, contact info
   - Shows "Guest Checkout" when no customer

6. **CashierInterface Page** (`/pages/CashierInterface.jsx`)
   - Complete integration example
   - Polls for customer data updates (2-second interval)
   - Shows loading state during customer lookup

## ✅ Flow Implementation

### Plugin ACTIVE Flow:
```
1. Cashier sees plugin toggle (ON)
2. Customer ID input field appears
3. Cashier enters customer identifier
4. Clicks "Start New Basket"
5. GraphQL mutation includes customerIdentifier
6. Backend publishes basket.started event
7. Customer lookup plugin processes event
8. Plugin calls mock API
9. Plugin publishes customer data back to event bus
10. Consumer updates basket with customer info
11. Frontend polls and displays customer data
```

### Plugin INACTIVE Flow:
```
1. Cashier sees plugin toggle (OFF)
2. No customer ID input field
3. Clicks "Start New Basket"
4. GraphQL mutation without customerIdentifier
5. Basket created as guest checkout
6. No customer lookup occurs
```

## ✅ Key Features

- **Dynamic UI**: Customer input only shows when plugin is active
- **Real-time Updates**: Polling catches customer data when it arrives
- **Plugin Control**: Cashier can toggle plugin on/off
- **Graceful Fallback**: Works with or without customer data
- **Loading States**: Shows appropriate feedback during lookup
- **Event-Driven**: Uses existing Kafka event architecture

## ✅ Usage

```jsx
import CashierInterface from './pages/CashierInterface';

function App() {
  return <CashierInterface employeeId={1} terminalId="TERMINAL_001" />;
}
```

## ✅ API Endpoints Used

- `plugins` query - Check plugin status
- `updatePlugin` mutation - Toggle plugin
- `startBasket` mutation - Create basket with optional customer
- `basket` query - Get basket with customer data

## ✅ Testing

The implementation allows cashiers to:
1. Toggle customer lookup plugin on/off
2. See immediate UI changes (input field appears/disappears)
3. Test customer lookup with mock data (+1234567890, john@example.com, etc.)
4. Observe customer data appearing in basket after lookup
5. Switch between customer and guest checkout modes

All components are minimal, focused, and integrate with existing GraphQL infrastructure.