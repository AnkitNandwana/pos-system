import React from 'react';
import { useQuery } from '@apollo/client/react';
import { HEALTH_CHECK } from './graphql/queries';
import './App.css';

interface HealthCheckData {
  __schema: {
    types: { name: string }[];
  };
}

function App() {
  const { loading, error, data } = useQuery<HealthCheckData>(HEALTH_CHECK);

  if (loading) return <p>Connecting to GraphQL...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div className="App">
      <header className="App-header">
        <h1>POS System Frontend</h1>
        <p>✅ GraphQL Connection Successful</p>
        <p>Available Types: {data?.__schema?.types?.length || 0}</p>
      </header>
    </div>
  );
}

export default App;
