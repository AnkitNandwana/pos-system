import React, { useEffect, useState } from 'react';
import { useMutation } from '@apollo/client/react';
import { START_BASKET_MUTATION } from '../graphql/mutations';
import { Employee, Terminal, Basket } from '../types';
import SessionHeader from './SessionHeader';
import BasketStatus from './BasketStatus';
import PluginsPage from './PluginsPage';
import {
  Container,
  Typography,
  Box,
  Paper,
  Alert
} from '@mui/material';
import { CheckCircle, Store } from '@mui/icons-material';

interface POSTerminalProps {
  employee: Employee;
  terminal: Terminal;
  onLogout: () => void;
}

interface StartBasketMutationData {
  startBasket: Basket;
}

const POSTerminal: React.FC<POSTerminalProps> = ({ employee, terminal, onLogout }) => {
  const [basket, setBasket] = React.useState<Basket | null>(null);
  const [currentView, setCurrentView] = useState<'terminal' | 'plugins'>('terminal');

  const [startBasket, { loading: basketLoading }] = useMutation<StartBasketMutationData>(START_BASKET_MUTATION, {
    onCompleted: (data) => {
      setBasket(data.startBasket);
    },
    onError: (error) => {
      console.error('Failed to start basket:', error);
    }
  });

  useEffect(() => {
    if (currentView === 'terminal') {
      startBasket({
        variables: {
          employeeId: parseInt(employee.id.toString()),
          terminalId: terminal.terminalId
        }
      });
    }
  }, [employee.id, terminal.terminalId, startBasket, currentView]);

  const handleLogout = () => {
    setBasket(null);
    onLogout();
  };

  const handlePluginsClick = () => {
    setCurrentView('plugins');
  };

  const handleBackToTerminal = () => {
    setCurrentView('terminal');
  };

  if (currentView === 'plugins') {
    return (
      <div className="min-h-screen bg-gray-50">
        <SessionHeader
          employee={employee}
          terminal={terminal}
          onLogout={handleLogout}
        />
        <div className="p-4">
          <button
            onClick={handleBackToTerminal}
            className="mb-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            ← Back to Terminal
          </button>
        </div>
        <PluginsPage />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <SessionHeader
        employee={employee}
        terminal={terminal}
        onLogout={handleLogout}
        onPluginsClick={handlePluginsClick}
      />
      
      <Container maxWidth="lg" className="py-8">
        <Box className="text-center mb-8">
          <Store className="text-6xl text-blue-600 mb-4" />
          <Typography variant="h3" className="font-bold text-gray-800 mb-2">
            POS Terminal Ready
          </Typography>
          <Typography variant="h6" className="text-gray-600">
            Terminal {terminal.terminalId} is active and ready for transactions
          </Typography>
        </Box>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <BasketStatus basket={basket} loading={basketLoading} />
          </div>
          
          <div>
            {basket && (
              <Paper className="p-6 shadow-lg border-l-4 border-blue-500">
                <Box className="flex items-center space-x-2 mb-4">
                  <CheckCircle className="text-green-600" />
                  <Typography variant="h6" className="font-semibold">
                    System Status
                  </Typography>
                </Box>
                
                <Alert severity="success" className="mb-4">
                  Terminal is operational and ready for transactions
                </Alert>
                
                <Box className="space-y-3">
                  <Typography variant="body1" className="flex items-center justify-between">
                    <span className="text-gray-600">Active Basket:</span>
                    <span className="font-mono font-semibold">{basket.basketId}</span>
                  </Typography>
                  
                  <Typography variant="body1" className="flex items-center justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className="text-green-600 font-semibold">Ready for Items</span>
                  </Typography>
                  
                  <Typography variant="body1" className="flex items-center justify-between">
                    <span className="text-gray-600">Terminal:</span>
                    <span className="font-semibold">{terminal.terminalId}</span>
                  </Typography>
                </Box>
              </Paper>
            )}
          </div>
        </div>
      </Container>
    </div>
  );
};

export default POSTerminal;