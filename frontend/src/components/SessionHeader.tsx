import React from 'react';
import { useMutation } from '@apollo/client';
import { LOGOUT_MUTATION } from '../graphql/mutations';
import { Employee, Terminal } from '../types';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Chip,
  Avatar,
  CircularProgress
} from '@mui/material';
import { Logout as LogoutIcon, Person, Computer, Settings, ArrowBack } from '@mui/icons-material';

interface SessionHeaderProps {
  employee: Employee;
  terminal: Terminal;
  onLogout: () => void;
  onPluginsClick?: () => void;
  onBackToTerminal?: () => void;
  currentView?: 'landing' | 'basket' | 'plugins';
}

const SessionHeader: React.FC<SessionHeaderProps> = ({ 
  employee, 
  terminal, 
  onLogout, 
  onPluginsClick, 
  onBackToTerminal,
  currentView 
}) => {
  const [logout, { loading }] = useMutation(LOGOUT_MUTATION, {
    onCompleted: () => {
      localStorage.removeItem('token');
      onLogout();
    },
    onError: (error: any) => {
      console.error('Logout error:', error);
      localStorage.removeItem('token');
      onLogout();
    }
  });

  const handleLogout = () => {
    logout({ variables: { terminalId: terminal.terminalId } });
  };

  return (
    <AppBar position="static" className="bg-gradient-to-r from-blue-600 to-blue-800">
      <Toolbar className="justify-between">
        <Box className="flex items-center space-x-4">
          <Avatar className="bg-blue-200 text-blue-800">
            <Person />
          </Avatar>
          <Box>
            <Typography variant="h6" className="font-semibold">
              {employee.firstName} {employee.lastName}
            </Typography>
            <Box className="flex items-center space-x-2 mt-1">
              <Chip 
                label={employee.role} 
                size="small" 
                className="bg-blue-100 text-blue-800"
              />
              <Chip 
                icon={<Computer />}
                label={terminal.terminalId}
                size="small"
                variant="outlined"
                className="text-white border-white"
              />
            </Box>
          </Box>
        </Box>
        
        <Box className="flex items-center space-x-4">
          <Typography variant="body2" className="text-blue-100">
            Login: {new Date(terminal.loginTime).toLocaleTimeString()}
          </Typography>
          
          {currentView === 'plugins' && onBackToTerminal && (
            <Button
              variant="outlined"
              onClick={onBackToTerminal}
              startIcon={<ArrowBack />}
              className="text-white border-white hover:bg-blue-700"
            >
              Back to Terminal
            </Button>
          )}
          
          {currentView !== 'plugins' && onPluginsClick && (
            <Button
              variant="contained"
              onClick={onPluginsClick}
              startIcon={<Settings />}
              className="bg-green-600 hover:bg-green-700 text-white font-semibold"
            >
              Plugins
            </Button>
          )}
          
          <Button
            variant="contained"
            color="error"
            onClick={handleLogout}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={16} /> : <LogoutIcon />}
            className="font-semibold"
          >
            {loading ? 'Logging out...' : 'Logout'}
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default SessionHeader;