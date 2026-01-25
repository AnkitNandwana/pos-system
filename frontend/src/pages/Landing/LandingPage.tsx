import React from 'react';
import { Container, Typography, Box, Button, Paper } from '@mui/material';
import { Store, ShoppingCart } from '@mui/icons-material';
import { Employee, Terminal } from '../../types';

interface LandingPageProps {
  employee: Employee;
  terminal: Terminal;
  onStartBasket: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ employee, terminal, onStartBasket }) => {
  return (
    <Container maxWidth="md" className="py-12">
      <Box className="text-center mb-8">
        <Store className="text-8xl text-blue-600 mb-6" />
        <Typography variant="h3" className="font-bold text-gray-800 mb-4">
          Welcome, {employee.firstName}!
        </Typography>
        <Typography variant="h6" className="text-gray-600 mb-2">
          Terminal {terminal.terminalId} is ready
        </Typography>
        <Typography variant="body1" className="text-gray-500">
          Ready to serve customers
        </Typography>
      </Box>

      <Paper className="p-8 text-center shadow-lg">
        <ShoppingCart className="text-6xl text-green-600 mb-4" />
        <Typography variant="h5" className="font-semibold mb-4">
          Ready to Start a New Transaction?
        </Typography>
        <Typography variant="body1" className="text-gray-600 mb-6">
          Click below to begin a new customer transaction
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={onStartBasket}
          className="px-8 py-3 text-lg"
          startIcon={<ShoppingCart />}
        >
          Start New Basket
        </Button>
      </Paper>
    </Container>
  );
};

export default LandingPage;