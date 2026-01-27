# Real-time Session Management Implementation

## Overview
This implementation provides real-time session management that automatically logs out users when they login from another tab/window.

## Backend Components

### 1. WebSocket Consumer (`events/session_consumer.py`)
- Handles WebSocket connections for session monitoring
- Listens for session termination events
- Sends real-time notifications to connected clients

### 2. Updated Login Mutation (`employees/mutations.py`)
- Terminates existing active sessions when user logs in
- Sends WebSocket notifications to terminated sessions
- Uses Django Channels to broadcast session termination

### 3. WebSocket Routing (`events/routing.py`)
- Added route: `ws/session/{terminal_id}/`
- Connects session consumer to WebSocket endpoint

## Frontend Components

### 1. Session Monitor Hook (`hooks/useSessionMonitor.ts`)
- Manages WebSocket connection for session monitoring
- Handles reconnection logic
- Triggers callback when session is terminated

### 2. Updated App Component (`App.tsx`)
- Integrates session monitoring
- Shows session termination dialog
- Handles automatic logout when session is terminated

## How It Works

1. **User Login**: When employee logs in, backend checks for existing active sessions
2. **Session Termination**: If active sessions exist, they are marked inactive and WebSocket notification is sent
3. **Real-time Notification**: Frontend receives WebSocket message about session termination
4. **User Notification**: Dialog appears informing user about session termination
5. **Automatic Logout**: User is automatically logged out and redirected to login page

## Testing

### Manual Testing
1. Start Django server: `python manage.py runserver`
2. Start Kafka consumer: `python manage.py consume_events`
3. Open frontend in two browser tabs
4. Login with same credentials in both tabs
5. First tab should show session terminated dialog

### Command Line Testing
```bash
# Test WebSocket functionality
python manage.py test_session_termination <terminal_id>
```

### Test Script
```bash
./test_session_management.sh
```

## Configuration Requirements

### Backend
- Redis server running (for Channels layer)
- Kafka server running (for event publishing)
- Django Channels configured in settings

### Frontend
- WebSocket support in browser
- Real-time connection to backend

## Error Handling

- WebSocket reconnection on connection loss
- Graceful fallback if WebSocket fails
- Console logging for debugging

## Security Considerations

- WebSocket connections are authenticated
- Session termination is server-side enforced
- JWT tokens are invalidated on logout