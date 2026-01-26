import { useMutation } from '@apollo/client';
import { useBasket } from '../context/BasketContext';
import { usePluginStatus } from './usePluginStatus';
import { ADD_ITEM_MUTATION } from '../graphql/mutations';

export const useProductAddition = () => {
  const { state, dispatch } = useBasket();
  const { pluginStatus } = usePluginStatus();
  const [addItemMutation] = useMutation(ADD_ITEM_MUTATION);

  const addProduct = async (product: {
    productId: string;
    name: string;
    price: number;
    quantity?: number;
  }) => {
    const isAgeVerificationActive = pluginStatus?.['age_verification'] || false;
    const terminalId = localStorage.getItem('terminal') ? JSON.parse(localStorage.getItem('terminal')!).terminalId : null;
    
    if (!isAgeVerificationActive) {
      // Direct addition - plugin inactive
      try {
        const result = await addItemMutation({
          variables: {
            basketId: state.basket?.basketId,
            productId: product.productId,
            productName: product.name,
            quantity: product.quantity || 1,
            price: product.price,
            terminalId: terminalId
          }
        });
        
        if (result.data?.addItem) {
          dispatch({ type: 'ADD_ITEM', payload: result.data.addItem });
        }
      } catch (error) {
        console.error('Error adding item:', error);
        dispatch({ type: 'SET_ERROR', payload: 'Failed to add item' });
      }
      return;
    }
    
    // Plugin active - event-driven flow
    dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'pending' });
    
    try {
      const result = await addItemMutation({
        variables: {
          basketId: state.basket?.basketId,
          productId: product.productId,
          productName: product.name,
          quantity: product.quantity || 1,
          price: product.price,
          terminalId: terminalId
        }
      });
      
      // If item was added directly (not age-restricted), reset state
      if (result.data?.addItem) {
        dispatch({ type: 'ADD_ITEM', payload: result.data.addItem });
        dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'idle' });
      } else {
        // Age-restricted item detected (null response), wait for verification events
        console.log('Age-restricted item detected, waiting for verification events');
      }
      
      // Reset pending state after 2 seconds if no verification event received
      setTimeout(() => {
        if (state.verificationState === 'pending') {
          dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'idle' });
        }
      }, 2000);
      
    } catch (error) {
      console.error('Error adding item:', error);
      dispatch({ type: 'SET_VERIFICATION_STATE', payload: 'idle' });
      dispatch({ type: 'SET_ERROR', payload: 'Failed to add item' });
    }
  };

  return { addProduct };
};