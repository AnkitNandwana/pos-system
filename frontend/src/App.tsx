import React, { useState, useEffect, useCallback } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography } from '@mui/material';
import { BasketProvider } from './context/BasketContext';
import LoginPage from './components/LoginPage';
import SessionHeader from './components/SessionHeader';
import LandingPage from './pages/Landing/LandingPage';
import BasketPage from './pages/Basket/BasketPage';
import StartBasketModal from './components/StartBasketModal';
import PluginsPage from './components/PluginsPage';
import FraudAlertDialog from './components/FraudAlertDialog';

import { Employee, Terminal, LoginResponse, Basket } from './types';
import { useBasket } from './context/BasketContext';
// import { useSessionMonitor } from './hooks/useSessionMonitor';
import { useFraudDetection } from './hooks/useFraudDetection';
import './App.css';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

function AppContent() {
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [terminal, setTerminal] = useState<Terminal | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentView, setCurrentView] = useState<'landing' | 'basket' | 'plugins'>('landing');
  const [showStartBasket, setShowStartBasket] = useState(false);
  const [showSessionTerminated, setShowSessionTerminated] = useState(false);
  const [fraudAlert, setFraudAlert] = useState<any>(null);
  const [showFraudAlert, setShowFraudAlert] = useState(false);
  
  const { state, dispatch } = useBasket();

  const handleFraudAlert = useCallback((alert: any) => {
    setFraudAlert(alert);
    setShowFraudAlert(true);
  }, []);

  const handleFraudAlertAcknowledge = useCallback(() => {
    setShowFraudAlert(false);
    setFraudAlert(null);
  }, []);

  const handleSessionTerminated = useCallback(() => {
    setShowSessionTerminated(true);
  }, []);

  const handleSessionTerminatedClose = useCallback(() => {
    setShowSessionTerminated(false);
    handleLogout();
  }, []);

  // Monitor fraud detection
  const { isConnected } = useFraudDetection({
    terminalId: terminal?.terminalId || null,
    onFraudAlert: handleFraudAlert,
    enabled: isLoggedIn
  });

  console.log('Fraud detection WebSocket connected:', isConnected, 'Terminal ID:', terminal?.terminalId);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedEmployee = localStorage.getItem('employee');
    const savedTerminal = localStorage.getItem('terminal');
    
    if (token && savedEmployee && savedTerminal) {
      setEmployee(JSON.parse(savedEmployee));
      setTerminal(JSON.parse(savedTerminal));
      setIsLoggedIn(true);
    }
  }, []);

  const handleLoginSuccess = (loginData: LoginResponse) => {
    setEmployee(loginData.employee);
    setTerminal(loginData.terminal);
    setIsLoggedIn(true);
    
    localStorage.setItem('employee', JSON.stringify(loginData.employee));
    localStorage.setItem('terminal', JSON.stringify(loginData.terminal));
  };

  const handleLogout = () => {
    setEmployee(null);
    setTerminal(null);
    setIsLoggedIn(false);
    setCurrentView('landing');
    dispatch({ type: 'CLEAR_BASKET' });
    
    localStorage.removeItem('token');
    localStorage.removeItem('employee');
    localStorage.removeItem('terminal');
  };

  const handleStartBasket = () => {
    setShowStartBasket(true);
  };

  const handleBasketCreated = (basket: Basket) => {
    dispatch({ type: 'SET_BASKET', payload: basket });
    if (basket.customer) {
      dispatch({ type: 'SET_CUSTOMER', payload: basket.customer });
    }
    setCurrentView('basket');
    setShowStartBasket(false);
  };

  if (!isLoggedIn || !employee || !terminal) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <SessionHeader
        employee={employee}
        terminal={terminal}
        onLogout={handleLogout}
        onPluginsClick={() => setCurrentView('plugins')}
        onBackToTerminal={() => setCurrentView(state.basket ? 'basket' : 'landing')}
        currentView={currentView}
      />
      
      {currentView === 'landing' && (
        <LandingPage
          employee={employee}
          terminal={terminal}
          onStartBasket={handleStartBasket}
        />
      )}
      
      {currentView === 'basket' && <BasketPage />}
      
      {currentView === 'plugins' && <PluginsPage />}

      <StartBasketModal
        open={showStartBasket}
        onClose={() => setShowStartBasket(false)}
        employee={employee}
        terminal={terminal}
        onBasketCreated={handleBasketCreated}
      />

      {/* Session Terminated Dialog */}
      <Dialog open={showSessionTerminated} maxWidth="sm" fullWidth>
        <DialogTitle>Session Terminated</DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            Your session has been terminated because you logged in from another location.
            Please log in again to continue.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSessionTerminatedClose} variant="contained" color="primary">
            OK
          </Button>
        </DialogActions>
      </Dialog>

      {/* Fraud Alert Dialog */}
      <FraudAlertDialog
        open={showFraudAlert}
        alert={fraudAlert}
        onAcknowledge={handleFraudAlertAcknowledge}
      />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BasketProvider>
        <AppContent />
      </BasketProvider>
    </ThemeProvider>
  );
}

export default App;
