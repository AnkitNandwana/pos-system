import { useQuery } from '@apollo/client';
import { useEffect, useState } from 'react';
import { GET_BASKET_DETAILS } from '../graphql/queries';
import { useBasket } from '../context/BasketContext';

export const useBasketDetails = (basketId: string | null) => {
  const { dispatch } = useBasket();
  const [hasCustomer, setHasCustomer] = useState(false);
  
  const { data, loading, error } = useQuery(GET_BASKET_DETAILS, {
    variables: { basketId: basketId || '' },
    skip: !basketId,
    pollInterval: hasCustomer ? 0 : 2000, // Stop polling once customer is found
    fetchPolicy: 'cache-and-network'
  });

  useEffect(() => {
    if (data?.basketDetails) {
      const basketData = data.basketDetails;
      
      // Update basket in context
      dispatch({
        type: 'SET_BASKET',
        payload: {
          basketId: basketData.basketId,
          status: basketData.status,
          customerId: basketData.customerId,
          items: basketData.items,
          totalAmount: basketData.totalAmount,
          employee: basketData.employee || { id: 0, username: 'unknown' }
        }
      });

      // Update customer in context
      dispatch({
        type: 'SET_CUSTOMER',
        payload: basketData.customer
      });
      
      // Stop polling if customer data is received
      if (basketData.customer) {
        setHasCustomer(true);
      }
    }
  }, [data, dispatch]);

  return { loading, error };
};