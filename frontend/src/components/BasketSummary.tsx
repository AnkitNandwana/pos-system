import React from 'react';
import { useMutation } from '@apollo/client';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Box,
  Button,
  Divider
} from '@mui/material';
import { Remove, Add, Delete } from '@mui/icons-material';
import { REMOVE_ITEM_MUTATION, UPDATE_QUANTITY_MUTATION } from '../graphql/mutations';
import { useBasket } from '../context/BasketContext';
import { Basket } from '../types';

interface BasketSummaryProps {
  basket: Basket;
}

const BasketSummary: React.FC<BasketSummaryProps> = ({ basket }) => {
  const { dispatch } = useBasket();
  
  const [removeItem] = useMutation(REMOVE_ITEM_MUTATION);
  const [updateQuantity] = useMutation(UPDATE_QUANTITY_MUTATION, {
    onCompleted: (data: any) => {
      dispatch({
        type: 'UPDATE_QUANTITY',
        payload: { itemId: data.updateQuantity.id, quantity: data.updateQuantity.quantity }
      });
    }
  });

  const handleRemoveItem = (itemId: string) => {
    removeItem({
      variables: { basketId: basket.basketId, itemId }
    });
    dispatch({ type: 'REMOVE_ITEM', payload: itemId });
  };

  const handleUpdateQuantity = (itemId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      handleRemoveItem(itemId);
      return;
    }
    
    updateQuantity({
      variables: { basketId: basket.basketId, itemId, quantity: newQuantity }
    });
  };

  return (
    <Paper className="p-4">
      <Typography variant="h6" className="mb-3">
        Basket Summary
      </Typography>
      
      <Typography variant="body2" className="text-gray-600 mb-4">
        Basket ID: {basket.basketId}
      </Typography>

      <List>
        {basket.items.map((item) => (
          <ListItem key={item.id} divider>
            <ListItemText
              primary={item.productName}
              secondary={`$${item.price} each`}
            />
            <ListItemSecondaryAction>
              <Box className="flex items-center space-x-2">
                <IconButton
                  size="small"
                  onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                >
                  <Remove />
                </IconButton>
                <Typography className="min-w-[2rem] text-center">
                  {item.quantity}
                </Typography>
                <IconButton
                  size="small"
                  onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                >
                  <Add />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => handleRemoveItem(item.id)}
                  color="error"
                >
                  <Delete />
                </IconButton>
              </Box>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>

      <Divider className="my-4" />
      
      <Box className="flex justify-between items-center mb-4">
        <Typography variant="h6">Total:</Typography>
        <Typography variant="h6" className="font-bold">
          ${basket.totalAmount.toFixed(2)}
        </Typography>
      </Box>

      <Button
        variant="contained"
        fullWidth
        size="large"
        disabled={basket.items.length === 0 || basket.status === 'PAID'}
        onClick={() => {
          dispatch({ type: 'SHOW_PAYMENT_MODAL', payload: true });
        }}
      >
        {basket.status === 'PAID' ? 'Basket Completed' : 'Checkout'}
      </Button>
    </Paper>
  );
};

export default BasketSummary;