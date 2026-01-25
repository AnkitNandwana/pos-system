import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import LoginPage from './components/LoginPage';
import POSTerminal from './components/POSTerminal';
import { Employee, Terminal, LoginResponse } from './types';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [terminal, setTerminal] = useState<Terminal | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

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
    
    localStorage.removeItem('token');
    localStorage.removeItem('employee');
    localStorage.removeItem('terminal');
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {!isLoggedIn || !employee || !terminal ? (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      ) : (
        <POSTerminal
          employee={employee}
          terminal={terminal}
          onLogout={handleLogout}
        />
      )}
    </ThemeProvider>
  );
}

export default App;
