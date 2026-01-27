# Real-time Purchase Recommendations Implementation

## What's Been Implemented

### Backend Changes

1. **GraphQL Subscriptions Support**
   - Updated `schema.py` to include `RecommendationSubscriptions`
   - Modified `plugins/purchase_recommender/subscriptions.py` to listen to Kafka events
   - Updated `config/asgi.py` to support GraphQL WebSocket subscriptions

2. **Plugin Status Checking**
   - Purchase recommender plugin already checks if it's enabled before processing events
   - If plugin is disabled, no recommendations are generated

3. **Improved Mutations**
   - Updated `plugins/purchase_recommender/mutations.py` to return success/error responses
   - Added proper error handling for accept/reject operations

### Frontend Changes

1. **WebSocket Support**
   - Updated `apollo/client.ts` to support GraphQL subscriptions over WebSocket
   - Added `graphql-ws` dependency to `package.json`

2. **Real-time Recommendations Component**
   - Updated `components/RealtimeRecommendations.tsx` to use GraphQL subscriptions
   - Replaced SSE with GraphQL subscription for real-time updates

3. **GraphQL Queries & Subscriptions**
   - Created `graphql/subscriptions.ts` with recommendation subscription
   - Updated `graphql/queries.ts` with accept/reject mutations

## How It Works

1. **Item Addition Triggers Event**
   - When employee adds item to basket, `ITEM_ADDED` event is published to Kafka

2. **Plugin Processes Event**
   - Purchase recommender plugin listens for `ITEM_ADDED` events
   - Checks if plugin is enabled (if disabled, stops processing)
   - Generates recommendations based on hardcoded rules or database rules
   - Publishes `RECOMMENDATION_SUGGESTED` event back to Kafka

3. **Real-time Display**
   - Frontend subscribes to recommendations via GraphQL WebSocket
   - `RecommendationSubscriptions` listens to Kafka for `RECOMMENDATION_SUGGESTED` events
   - Recommendations appear instantly in the UI

4. **User Actions**
   - Employee can accept (adds item to basket) or reject recommendations
   - Actions are processed via GraphQL mutations
   - UI updates immediately

## Testing Steps

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Services**
   ```bash
   # Terminal 1 - Django
   python manage.py runserver
   
   # Terminal 2 - Kafka Consumer
   python manage.py consume_events
   
   # Terminal 3 - Frontend
   cd frontend && npm start
   ```

3. **Enable Plugin**
   - Go to Django admin: http://localhost:8000/admin
   - Ensure `purchase_recommender` plugin is enabled

4. **Test Flow**
   - Login to POS system
   - Start a basket
   - Add items like "BURGER", "COFFEE", "LAPTOP" to trigger recommendations
   - Recommendations should appear in real-time
   - Test accept/reject functionality

## Plugin Disable Behavior

- When plugin is disabled in Django admin, it won't process `ITEM_ADDED` events
- No recommendations will be generated or displayed
- UI will show "No recommendations available"

## Troubleshooting

- Check browser console for WebSocket connection errors
- Verify Kafka consumer is running and processing events
- Check Django logs for plugin processing messages
- Ensure GraphQL WebSocket endpoint is accessible at `ws://localhost:8000/graphql/`