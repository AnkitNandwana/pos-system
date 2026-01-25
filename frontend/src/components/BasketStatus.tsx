import React from 'react';
import { Basket } from '../types';
import { useBasket } from '../context/BasketContext';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Divider,
  Alert
} from '@mui/material';
import { ShoppingCart, Person, CheckCircle, Warning, HourglassEmpty } from '@mui/icons-material';

interface BasketStatusProps {
  basket: Basket | null;
  loading: boolean;
}

const BasketStatus: React.FC<BasketStatusProps> = ({ basket, loading }) => {
  const { state } = useBasket();
  
  const getVerificationStateDisplay = () => {
    switch (state.verificationState) {
      case 'pending':
        return (
          <Alert severity="info" icon={<HourglassEmpty />} className="mb-4">
            Processing item addition...
          </Alert>
        );
      case 'required':
        return (
          <Alert severity="warning" icon={<Warning />} className="mb-4">
            Age verification required
          </Alert>
        );
      case 'verifying':
        return (
          <Alert severity="info" className="mb-4">
            Verifying customer age...
          </Alert>
        );
      case 'failed':
        return (
          <Alert severity="error" className="mb-4">
            Verification failed or cancelled
          </Alert>
        );
      default:
        return null;
    }
  };
  if (loading) {
    return (
      <Card className="m-6 shadow-lg">
        <CardContent className="text-center py-8">
          <CircularProgress className="mb-4" />
          <Typography variant="h6" className="text-gray-600">
            Starting new basket...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (!basket) {
    return (
      <Card className="m-6 shadow-lg">
        <CardContent className="text-center py-8">
          <ShoppingCart className="text-6xl text-gray-400 mb-4" />
          <Typography variant="h6" className="text-gray-600">
            No active basket
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="m-6 shadow-lg border-l-4 border-green-500">
      <CardContent>
        <Box className="flex items-center justify-between mb-4">
          <Box className="flex items-center space-x-2">
            <ShoppingCart className="text-green-600" />
            <Typography variant="h6" className="font-semibold">
              Current Basket
            </Typography>
          </Box>
          <Chip 
            icon={<CheckCircle />}
            label={basket.status}
            color="success"
            variant="outlined"
          />
        </Box>
        
        <Divider className="mb-4" />
        
        {getVerificationStateDisplay()}
        
        <Box className="space-y-3">
          <Box className="flex justify-between items-center">
            <Typography variant="body2" className="text-gray-600">
              Basket ID:
            </Typography>
            <Typography variant="body1" className="font-mono font-semibold">
              {basket.basketId}
            </Typography>
          </Box>
          
          <Box className="flex justify-between items-center">
            <Typography variant="body2" className="text-gray-600">
              Cashier:
            </Typography>
            <Box className="flex items-center space-x-1">
              <Person className="text-sm" />
              <Typography variant="body1">
                {basket.employee.username}
              </Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BasketStatus;