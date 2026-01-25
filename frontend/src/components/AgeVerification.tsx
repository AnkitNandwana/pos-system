import React, { useState, useEffect } from 'react';
import { useSubscription, useMutation } from '@apollo/client';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  List,
  ListItem,
  ListItemText,
  Box,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Warning, CheckCircle, Cancel } from '@mui/icons-material';
import { AGE_VERIFICATION_SUBSCRIPTION } from '../graphql/subscriptions';
import { VERIFY_AGE_MUTATION, CANCEL_AGE_VERIFICATION_MUTATION, ADD_VERIFIED_ITEM_MUTATION } from '../graphql/mutations';
import { useBasket } from '../context/BasketContext';

const AgeVerification: React.FC = () => {
  const { state, dispatch } = useBasket();
  const { basket } = state;
  const [customerAge, setCustomerAge] = useState<string>('');
  const [verificationMethod, setVerificationMethod] = useState<string>('MANUAL_CHECK');

  const [verifyAge] = useMutation(VERIFY_AGE_MUTATION);
  const [cancelVerification] = useMutation(CANCEL_AGE_VERIFICATION_MUTATION);
  const [addVerifiedItem] = useMutation(ADD_VERIFIED_ITEM_MUTATION);

  // Subscribe to verification events
  const { data } = useSubscription(AGE_VERIFICATION_SUBSCRIPTION, {
    variables: { basketId: basket?.basketId || '' },
    skip: !basket?.basketId,
    onData: ({ data }) => {
      const event = data.data?.ageVerificationEvents;
      
      switch (event?.eventType) {
        case 'age.verification.required':
          dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'required' });
          dispatch({ type: 'SET_PENDING_ITEMS', payload: event.restrictedItems });
          break;
          
        case 'age.verification.completed':
          dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'verified' });
          addVerifiedItems();
          break;
          
        case 'age.verification.failed':
          dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'failed' });
          dispatch({ type: 'CLEAR_PENDING_ITEMS' });
          break;
      }
    }
  });

  const addVerifiedItems = async () => {
    console.log('Adding verified items:', state.pendingItems);
    for (const item of state.pendingItems) {
      console.log('Processing item:', item, 'Price:', item.price);
      try {
        const result = await addVerifiedItem({
          variables: {
            basketId: basket?.basketId,
            productId: item.productId,
            productName: item.name,
            quantity: item.quantity || 1,
            price: parseFloat(String(item.price || 0)) || 0.0
          }
        });
        
        console.log('Add verified item result:', result.data?.addVerifiedItem);
        if (result.data?.addVerifiedItem) {
          dispatch({ type: 'ADD_ITEM', payload: result.data.addVerifiedItem });
        }
      } catch (error) {
        console.error('Error adding verified item:', error);
      }
    }
    dispatch({ type: 'CLEAR_PENDING_ITEMS' });
    dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'idle' });
  };

  const handleVerifyAge = async () => {
    if (!customerAge || !basket?.basketId) return;

    dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'verifying' });
    
    try {
      await verifyAge({
        variables: {
          basketId: basket.basketId,
          verifierEmployeeId: Number(basket.employee.id),
          customerAge: parseInt(customerAge),
          verificationMethod
        }
      });
    } catch (error) {
      console.error('Error verifying age:', error);
      dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'failed' });
    }
  };

  const handleCancel = async () => {
    if (!basket?.basketId) return;

    try {
      await cancelVerification({
        variables: {
          basketId: basket.basketId,
          employeeId: Number(basket.employee.id)
        }
      });
      
      dispatch({ type: 'CLEAR_PENDING_ITEMS' });
      dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'idle' });
      setCustomerAge('');
    } catch (error) {
      console.error('Error cancelling verification:', error);
    }
  };

  // Only show dialog when verification is required
  if (state.verificationState !== 'required' && state.verificationState !== 'verifying') {
    return null;
  }

  const minimumAge = Math.max(...state.pendingItems.map(item => item.minimumAge || 18));

  return (
    <Dialog open={true} maxWidth="md" fullWidth>
      <DialogTitle className="flex items-center space-x-2">
        <Warning className="text-orange-500" />
        <span>Age Verification Required</span>
      </DialogTitle>
      
      <DialogContent>
        <Alert severity="warning" className="mb-4">
          The following items require age verification before they can be added to the basket:
        </Alert>
        
        <List className="mb-4">
          {state.pendingItems.map((item, index) => (
            <ListItem key={index} className="bg-orange-50 mb-2 rounded">
              <ListItemText
                primary={item.name}
                secondary={`Minimum age: ${item.minimumAge} years | Category: ${item.category}`}
              />
            </ListItem>
          ))}
        </List>
        
        <Box className="space-y-4">
          <TextField
            fullWidth
            label="Customer Age"
            type="number"
            value={customerAge}
            onChange={(e) => setCustomerAge(e.target.value)}
            inputProps={{ min: 0, max: 120 }}
            helperText={`Minimum required age: ${minimumAge} years`}
          />
          
          <FormControl fullWidth>
            <InputLabel>Verification Method</InputLabel>
            <Select
              value={verificationMethod}
              onChange={(e) => setVerificationMethod(e.target.value)}
              label="Verification Method"
            >
              <MenuItem value="MANUAL_CHECK">Manual ID Check</MenuItem>
              <MenuItem value="ID_SCANNER">ID Scanner</MenuItem>
              <MenuItem value="BIOMETRIC">Biometric Verification</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button
          onClick={handleCancel}
          color="error"
          startIcon={<Cancel />}
        >
          Cancel & Remove Items
        </Button>
        <Button
          onClick={handleVerifyAge}
          variant="contained"
          color="success"
          startIcon={<CheckCircle />}
          disabled={!customerAge || parseInt(customerAge) < minimumAge || state.verificationState === 'verifying'}
        >
          {state.verificationState === 'verifying' ? 'Verifying...' : 'Verify Age'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AgeVerification;