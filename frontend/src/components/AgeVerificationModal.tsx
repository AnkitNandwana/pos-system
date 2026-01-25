import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
  Box
} from '@mui/material';
import { Warning } from '@mui/icons-material';
import { useBasket } from '../context/BasketContext';

interface AgeVerificationModalProps {
  open: boolean;
  productId?: string;
  minimumAge?: number;
}

const AgeVerificationModal: React.FC<AgeVerificationModalProps> = ({
  open,
  productId,
  minimumAge
}) => {
  const { dispatch } = useBasket();

  const handleVerify = () => {
    dispatch({
      type: 'SET_AGE_VERIFICATION',
      payload: { required: false, verified: true, productId, minimumAge }
    });
  };

  const handleCancel = () => {
    dispatch({
      type: 'SET_AGE_VERIFICATION',
      payload: { required: false, verified: false }
    });
  };

  return (
    <Dialog open={open} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box className="flex items-center space-x-2">
          <Warning className="text-orange-500" />
          <Typography variant="h6">Age Verification Required</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Alert severity="warning" className="mb-4">
          This product requires age verification
        </Alert>
        
        <Typography variant="body1" className="mb-4">
          Customer must be at least <strong>{minimumAge} years old</strong> to purchase this item.
        </Typography>
        
        <Typography variant="body2" className="text-gray-600">
          Please verify the customer's age by checking their ID before proceeding.
        </Typography>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleCancel} color="error">
          Cancel Purchase
        </Button>
        <Button onClick={handleVerify} variant="contained">
          Age Verified - Add to Basket
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AgeVerificationModal;