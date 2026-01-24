# POS System Frontend

React + Apollo Client frontend for the POS system.

## Setup Complete ✅

The frontend has been successfully configured with:
- React 19 with TypeScript
- Apollo Client for GraphQL
- Health check query to verify backend connection

## Project Structure

```
frontend/
├── src/
│   ├── apollo/
│   │   └── client.ts          # Apollo Client configuration
│   ├── graphql/
│   │   ├── queries.ts         # GraphQL queries
│   │   └── mutations.ts       # GraphQL mutations
│   ├── components/            # React components (empty)
│   ├── App.tsx               # Main App component with health check
│   └── index.tsx             # App entry point with ApolloProvider
├── package.json
└── start.sh                  # Custom start script for port 3001
```

## Running the Frontend

### Option 1: Using custom script (recommended)
```bash
./start.sh
```

### Option 2: Manual port setting
```bash
export PORT=3001 && npm start
```

### Option 3: Default port (if available)
```bash
npm start
```

## Verification

When the frontend starts successfully, you should see:
- ✅ GraphQL Connection Successful
- Available Types: [number] (shows GraphQL schema is accessible)

## Backend Requirements

Ensure the Django backend is running on `http://localhost:8000` with GraphQL endpoint at `/graphql/`.

## Next Steps

The frontend is ready for:
1. Employee login/logout components
2. POS terminal interface
3. Product management
4. Basket/cart functionality
5. Plugin-specific UI components

## Troubleshooting

- **Port conflicts**: Use `./start.sh` to run on port 3001
- **GraphQL errors**: Ensure backend is running and accessible
- **CORS issues**: Check Django CORS settings allow `localhost:3001`