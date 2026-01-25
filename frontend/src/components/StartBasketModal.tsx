import React, { useState } from 'react';
import { useMutation } from '@apollo/client/react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Typography,
  Box,
  CircularProgress,
  Alert
} from '@mui/material';
import { Person, Phone, CreditCard } from '@mui/icons-material';
import { START_BASKET_MUTATION } from '../graphql/mutations';
import { Employee, Terminal, Basket } from '../types';

interface StartBasketModalProps {
  open: boolean;
  onClose: () => void;
  employee: Employee;
  terminal: Terminal;
  onBasketCreated: (basket: Basket) => void;
}

const StartBasketModal: React.FC<StartBasketModalProps> = ({
  open,
  onClose,
  employee,
  terminal,
  onBasketCreated
}) => {
  const [customerIdentifier, setCustomerIdentifier] = useState('');
  const [identifierType, setIdentifierType] = useState<'phone' | 'loyalty' | 'guest'>('phone');

  const [startBasket, { loading, error }] = useMutation(START_BASKET_MUTATION, {
    onCompleted: (data: any) => {
      onBasketCreated(data.startBasket);
      onClose();
      setCustomerIdentifier('');
    }
  });

  const handleSubmit = () => {
    const identifier = identifierType === 'guest' ? null : customerIdentifier;
    startBasket({
      variables: {
        employeeId: parseInt(employee.id.toString()),
        terminalId: terminal.terminalId,
        customerIdentifier: identifier
      }
    });
  };

  const handleGuestCheckout = () => {
    setIdentifierType('guest');
    handleSubmit();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Typography variant="h5" className="font-semibold">
          Start New Basket
        </Typography>
      </DialogTitle>
      
      <DialogContent>
        <Box className="space-y-4 pt-2">
          <Typography variant="body1" className="text-gray-600">
            How would you like to identify the customer?
          </Typography>

          <Box className="grid grid-cols-1 gap-3">
            <Button
              variant={identifierType === 'phone' ? 'contained' : 'outlined'}
              onClick={() => setIdentifierType('phone')}
              startIcon={<Phone />}
              className="justify-start p-3"
            >
              Phone Number
            </Button>
            
            <Button
              variant={identifierType === 'loyalty' ? 'contained' : 'outlined'}
              onClick={() => setIdentifierType('loyalty')}
              startIcon={<CreditCard />}
              className="justify-start p-3"
            >
              Loyalty Card / Customer ID
            </Button>
          </Box>

          {identifierType !== 'guest' && (
            <TextField
              fullWidth
              label={identifierType === 'phone' ? 'Phone Number' : 'Customer ID'}
              value={customerIdentifier}
              onChange={(e) => setCustomerIdentifier(e.target.value)}
              placeholder={identifierType === 'phone' ? '+1234567890' : 'CUST123'}
              variant="outlined"
            />
          )}

          {error && (
            <Alert severity="error">
              {error.message}
            </Alert>
          )}
        </Box>
      </DialogContent>

      <DialogActions className="p-4 space-x-2">
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        
        <Button
          variant="outlined"
          onClick={handleGuestCheckout}
          disabled={loading}
          startIcon={<Person />}
        >
          Guest Checkout
        </Button>
        
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading || (!customerIdentifier && identifierType !== 'guest')}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          Start Basket
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StartBasketModal;