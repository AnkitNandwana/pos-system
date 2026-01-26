import React from 'react';
import { Container } from '@mui/material';
import { useMutation } from '@apollo/client';
import { useBasket } from '../../context/BasketContext';
import { useBasketDetails } from '../../hooks/useBasketDetails';
import { START_BASKET_MUTATION } from '../../graphql/mutations';
import ProductSearch from '../../components/ProductSearch';
import ProductList from '../../components/ProductList';
import BasketSummary from '../../components/BasketSummary';
import RealtimeRecommendations from '../../components/RealtimeRecommendations';
import AgeVerification from '../../components/AgeVerification';
import CustomerInfo from '../../components/CustomerInfo';
import PaymentModal from '../../components/PaymentModal';
import ThankYouScreen from '../../components/ThankYouScreen';

const BasketPage: React.FC = () => {
  const { state, dispatch } = useBasket();
  const { basket, customer, showPaymentModal, showThankYou } = state;
  
  // Fetch basket details with polling for customer updates
  useBasketDetails(basket?.basketId || null);

  const [startBasket] = useMutation(START_BASKET_MUTATION, {
    onCompleted: (data) => {
      dispatch({ type: 'SET_BASKET', payload: data.startBasket });
    }
  });

  if (!basket) {
    return (
      <Container>
        <div>No active basket</div>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" className="py-4">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Section */}
        <div className="lg:col-span-1 space-y-4">
          <CustomerInfo customer={customer} />
          <RealtimeRecommendations />
        </div>

        {/* Middle Section - Product Grid */}
        <div className="lg:col-span-1 space-y-4">
          <ProductSearch />
          <ProductList />
        </div>

        {/* Right Section - Basket Summary */}
        <div className="lg:col-span-1">
          <div className="mt-8">
            <BasketSummary basket={basket} />
          </div>
        </div>
      </div>

      <AgeVerification />
      
      {basket && (
        <>
          <PaymentModal
            open={showPaymentModal}
            onClose={() => dispatch({ type: 'SHOW_PAYMENT_MODAL', payload: false })}
            totalAmount={basket.totalAmount}
            basketId={basket.basketId}
            terminalId={localStorage.getItem('terminalId') || 'terminal-1'}
            employeeId={parseInt(localStorage.getItem('employeeId') || '1')}
          />
          
          <ThankYouScreen
            open={showThankYou}
            onStartNewBasket={() => {}}
            totalAmount={basket.totalAmount}
            basketId={basket.basketId}
          />
        </>
      )}
    </Container>
  );
};

export default BasketPage;