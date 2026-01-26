import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box
} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { useBasket } from '../context/BasketContext';

interface ThankYouScreenProps {
  open: boolean;
  onStartNewBasket: () => void;
  totalAmount: number;
  basketId: string;
}

const ThankYouScreen: React.FC<ThankYouScreenProps> = ({
  open,
  onStartNewBasket,
  totalAmount,
  basketId
}) => {
  const { dispatch } = useBasket();

  const handleStartNewBasket = () => {
    dispatch({ type: 'SHOW_THANK_YOU', payload: false });
    dispatch({ type: 'CLEAR_BASKET' });
    dispatch({ type: 'SET_PAYMENT_STATE', payload: 'idle' });
    // Redirect to landing page
    window.location.href = '/';
  };

  return (
    <Dialog open={open} maxWidth="sm" fullWidth>
      <DialogContent>
        <Box className="text-center space-y-4 py-8">
          <CheckCircleOutlineIcon 
            sx={{ fontSize: 80, color: 'success.main' }} 
          />
          
          <Typography variant="h4" className="font-bold text-green-600">
            Payment Successful!
          </Typography>
          
          <Typography variant="h6">
            Thank you for your purchase
          </Typography>
          
          <Box className="bg-gray-50 p-4 rounded-lg">
            <Typography variant="body1">
              <strong>Basket ID:</strong> {basketId}
            </Typography>
            <Typography variant="body1">
              <strong>Amount Paid:</strong> ${totalAmount.toFixed(2)}
            </Typography>
          </Box>
          
          <Typography variant="body2" className="text-gray-600">
            Your transaction has been completed successfully.
            The basket is now locked and read-only.
          </Typography>
        </Box>
      </DialogContent>
      <DialogActions className="justify-center pb-4">
        <Button
          onClick={handleStartNewBasket}
          variant="contained"
          size="large"
          className="px-8"
        >
          Back To Terminal
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ThankYouScreen;