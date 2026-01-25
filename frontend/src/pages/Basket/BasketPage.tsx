import React from 'react';
import { Container } from '@mui/material';
import { useBasket } from '../../context/BasketContext';
import ProductSearch from '../../components/ProductSearch';
import BasketSummary from '../../components/BasketSummary';
import RealtimeRecommendations from '../../components/RealtimeRecommendations';
import AgeVerification from '../../components/AgeVerification';
import CustomerInfo from '../../components/CustomerInfo';

const BasketPage: React.FC = () => {
  const { state } = useBasket();
  const { basket, customer, ageVerification } = state;

  if (!basket) {
    return (
      <Container>
        <div>No active basket</div>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" className="py-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1 space-y-4">
          <CustomerInfo customer={customer} />
          <ProductSearch />
          <RealtimeRecommendations />
        </div>

        <div className="md:col-span-2">
          <BasketSummary basket={basket} />
        </div>
      </div>

      <AgeVerification />
    </Container>
  );
};

export default BasketPage;