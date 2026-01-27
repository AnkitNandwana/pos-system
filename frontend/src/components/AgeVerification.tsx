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
import { VERIFY_AGE_MUTATION, CANCEL_AGE_VERIFICATION_MUTATION } from '../graphql/mutations';
import { useBasket } from '../context/BasketContext';

const AgeVerification: React.FC = () => {
  const { state, dispatch } = useBasket();
  const { basket } = state;
  const [customerAge, setCustomerAge] = useState<string>('');
  const [verificationMethod, setVerificationMethod] = useState<string>('MANUAL_CHECK');

  const [verifyAge] = useMutation(VERIFY_AGE_MUTATION);
  const [cancelVerification] = useMutation(CANCEL_AGE_VERIFICATION_MUTATION);

  // Subscribe to verification events
  const { data } = useSubscription(AGE_VERIFICATION_SUBSCRIPTION, {
    variables: { basketId: basket?.basketId || '' },
    skip: !basket?.basketId,
    onData: ({ data }) => {
      const event = data.data?.ageVerificationEvents;
      
      switch (event?.eventType) {
        case 'age.verification.required':
          console.log('=== AGE VERIFICATION DEBUG ===');
          console.log('Full event:', JSON.stringify(event, null, 2));
          console.log('Restricted items:', JSON.stringify(event.restrictedItems, null, 2));
          event.restrictedItems?.forEach((item: any, index: number) => {
            console.log(`Item ${index}:`, {
              name: item.name,
              minimumAge: item.minimumAge,
              minimum_age: item.minimum_age,
              allKeys: Object.keys(item)
            });
          });
          console.log('=== END DEBUG ===');
          dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'required' });
          dispatch({ type: 'SET_PENDING_ITEMS', payload: event.restrictedItems });
          break;
          
        case 'age.verification.completed':
          dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'verified' });
          dispatch({ type: 'CLEAR_PENDING_ITEMS' });
          dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'idle' });
          break;
          
        case 'age.verification.failed':
          dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'failed' });
          dispatch({ type: 'CLEAR_PENDING_ITEMS' });
          break;
      }
    }
  });

  const handleVerifyAge = async () => {
    if (!customerAge || !basket?.basketId) return;

    dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'verifying' });
    
    try {
      await verifyAge({
        variables: {
          basketId: basket.basketId,
          verifierEmployeeId: Number(basket.employee.id),
          customerAge: parseInt(customerAge),
          terminalId: localStorage.getItem('terminalId') || '',
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

  const minimumAge = state.pendingItems.length > 0 
    ? Math.max(...state.pendingItems.map(item => {
        console.log('Processing item for min age:', item);
        return item.minimumAge || item.minimum_age || 18;
      }))
    : 18;

  // If no pending items but we have verification event data, use event minimumAge
  const eventMinimumAge = data?.data?.ageVerificationEvents?.minimumAge;
  const finalMinimumAge = state.pendingItems.length === 0 && eventMinimumAge ? eventMinimumAge : minimumAge;

  console.log('Calculated minimum age:', finalMinimumAge, 'from items:', state.pendingItems, 'event age:', eventMinimumAge);

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
                secondary={`Minimum age: ${item.minimumAge || item.minimum_age || 18} years | Category: ${item.category}`}
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
            helperText={`Minimum required age: ${finalMinimumAge} years`}
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
          disabled={!customerAge || parseInt(customerAge) < finalMinimumAge || state.verificationState === 'verifying'}
        >
          {state.verificationState === 'verifying' ? 'Verifying...' : 'Verify Age'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AgeVerification;