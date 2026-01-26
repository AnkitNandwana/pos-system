import React from 'react';
import { Container, Typography, Box, Button, Paper, Card, CardContent } from '@mui/material';
import { Store, ShoppingCart, AccessTime, Person } from '@mui/icons-material';
import { Employee, Terminal } from '../../types';

interface LandingPageProps {
  employee: Employee;
  terminal: Terminal;
  onStartBasket: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ employee, terminal, onStartBasket }) => {
  console.log('Employee data:', employee);
  
  return (
    <div className="h-screen bg-gradient-to-br from-blue-50 to-indigo-100 overflow-hidden">
      <div className="h-full flex flex-col justify-center px-6 max-w-4xl mx-auto">
        {/* Welcome Header */}
        <div className="text-center mb-6">
          <div className="mb-4">
            <Store className="text-6xl text-blue-600 mb-3 drop-shadow-lg" />
          </div>
          <Typography variant="h3" className="font-bold text-gray-800 mb-3 tracking-tight">
            Welcome, {employee?.firstName && employee?.lastName 
              ? `${employee.firstName} ${employee.lastName}` 
              : employee?.username || 'User'}!
          </Typography>
          <Typography variant="h6" className="text-gray-600 mb-2 font-medium">
            Terminal is ready and operational
          </Typography>
          <Typography variant="body1" className="text-gray-500">
            Ready to serve customers with excellence
          </Typography>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <Card className="shadow-md">
            <CardContent className="p-4 text-center">
              <Person className="text-3xl text-blue-600 mb-2" />
              <Typography variant="h6" className="font-semibold mb-1 text-gray-800">
                Employee Status
              </Typography>
              <Typography variant="body2" className="text-gray-600 mb-1">
                Role: {employee?.role || 'N/A'}
              </Typography>
              <Typography variant="body2" className="text-green-600 font-medium">
                ✓ Active & Ready
              </Typography>
            </CardContent>
          </Card>
          <Card className="shadow-md">
            <CardContent className="p-4 text-center">
              <AccessTime className="text-3xl text-green-600 mb-2" />
              <Typography variant="h6" className="font-semibold mb-1 text-gray-800">
                Session Info
              </Typography>
              <Typography variant="body2" className="text-gray-600 mb-1">
                Login: {new Date(terminal?.loginTime || Date.now()).toLocaleTimeString()}
              </Typography>
              <Typography variant="body2" className="text-green-600 font-medium">
                ✓ Session Active
              </Typography>
            </CardContent>
          </Card>
        </div>

        {/* Main Action Card */}
        <Paper className="p-6 text-center shadow-xl rounded-2xl bg-white border border-gray-100">
          <div className="mb-4">
            <ShoppingCart className="text-5xl text-green-600 mb-3 drop-shadow-md" />
          </div>
          <Typography variant="h4" className="font-bold mb-3 text-gray-800">
            Ready to Start a New Transaction?
          </Typography>
          <Typography variant="body1" className="text-gray-600 mb-4">
            Click below to begin a new customer transaction
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={onStartBasket}
            className="px-6 py-2 text-lg font-semibold rounded-xl shadow-lg"
            startIcon={<ShoppingCart />}
            sx={{
              background: 'linear-gradient(45deg, #4CAF50 30%, #66BB6A 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #45a049 30%, #5cb85c 90%)',
              }
            }}
          >
            Start New Basket
          </Button>
        </Paper>
      </div>
    </div>
  );
};

export default LandingPage;