import React, { useState } from 'react';
import { useMutation } from '@apollo/client';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Typography,
  Box,
  CircularProgress
} from '@mui/material';
import { PROCESS_PAYMENT_MUTATION } from '../graphql/mutations';
import { useBasket } from '../context/BasketContext';

interface PaymentModalProps {
  open: boolean;
  onClose: () => void;
  totalAmount: number;
  basketId: string;
  terminalId: string;
  employeeId: number;
}

const PaymentModal: React.FC<PaymentModalProps> = ({
  open,
  onClose,
  totalAmount,
  basketId,
  terminalId,
  employeeId
}) => {
  const [paymentMethod, setPaymentMethod] = useState('CASH');
  const [processing, setProcessing] = useState(false);
  const { dispatch } = useBasket();

  const [processPayment] = useMutation(PROCESS_PAYMENT_MUTATION, {
    onCompleted: () => {
      setProcessing(false);
      dispatch({ type: 'SET_PAYMENT_STATE', payload: 'completed' });
      dispatch({ type: 'SHOW_PAYMENT_MODAL', payload: false });
      dispatch({ type: 'SHOW_THANK_YOU', payload: true });
      onClose();
    },
    onError: (error) => {
      setProcessing(false);
      dispatch({ type: 'SET_PAYMENT_STATE', payload: 'failed' });
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  });

  const handlePayment = async () => {
    setProcessing(true);
    dispatch({ type: 'SET_PAYMENT_STATE', payload: 'processing' });

    try {
      await processPayment({
        variables: {
          basketId,
          terminalId,
          employeeId,
          totalAmount,
          paymentMethod
        }
      });
    } catch (error) {
      console.error('Payment failed:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Payment</DialogTitle>
      <DialogContent>
        <Box className="space-y-4">
          <Typography variant="h6" className="text-center">
            Total Amount: ${totalAmount.toFixed(2)}
          </Typography>

          <FormControl component="fieldset">
            <FormLabel component="legend">Payment Method</FormLabel>
            <RadioGroup
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
            >
              <FormControlLabel value="CASH" control={<Radio />} label="Cash" />
              <FormControlLabel value="CARD" control={<Radio />} label="Card" />
              <FormControlLabel value="UPI" control={<Radio />} label="UPI" />
            </RadioGroup>
          </FormControl>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={processing}>
          Cancel
        </Button>
        <Button
          onClick={handlePayment}
          variant="contained"
          disabled={processing}
          startIcon={processing ? <CircularProgress size={20} /> : null}
        >
          {processing ? 'Processing...' : 'Pay Now'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PaymentModal;