import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Basket, Customer, BasketItem, AgeVerificationState, Recommendation } from '../types';

interface BasketState {
  basket: Basket | null;
  customer: Customer | null;
  ageVerification: AgeVerificationState;
  recommendations: Recommendation[];
  loading: boolean;
  error: string | null;
}

type BasketAction =
  | { type: 'SET_BASKET'; payload: Basket }
  | { type: 'SET_CUSTOMER'; payload: Customer | null }
  | { type: 'ADD_ITEM'; payload: BasketItem }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_QUANTITY'; payload: { itemId: string; quantity: number } }
  | { type: 'SET_RECOMMENDATIONS'; payload: Recommendation[] }
  | { type: 'SET_AGE_VERIFICATION'; payload: AgeVerificationState }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_BASKET' };

const initialState: BasketState = {
  basket: null,
  customer: null,
  ageVerification: { required: false, verified: false },
  recommendations: [],
  loading: false,
  error: null,
};

function basketReducer(state: BasketState, action: BasketAction): BasketState {
  switch (action.type) {
    case 'SET_BASKET':
      return { ...state, basket: action.payload };
    case 'SET_CUSTOMER':
      return { ...state, customer: action.payload };
    case 'ADD_ITEM':
      if (!state.basket) return state;
      return {
        ...state,
        basket: {
          ...state.basket,
          items: [...state.basket.items, action.payload],
          totalAmount: state.basket.totalAmount + (action.payload.price * action.payload.quantity)
        }
      };
    case 'REMOVE_ITEM':
      if (!state.basket) return state;
      const itemToRemove = state.basket.items.find(item => item.id === action.payload);
      return {
        ...state,
        basket: {
          ...state.basket,
          items: state.basket.items.filter(item => item.id !== action.payload),
          totalAmount: state.basket.totalAmount - (itemToRemove ? itemToRemove.price * itemToRemove.quantity : 0)
        }
      };
    case 'UPDATE_QUANTITY':
      if (!state.basket) return state;
      const updatedItems = state.basket.items.map(item => 
        item.id === action.payload.itemId 
          ? { ...item, quantity: action.payload.quantity }
          : item
      );
      const newTotal = updatedItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      return {
        ...state,
        basket: {
          ...state.basket,
          items: updatedItems,
          totalAmount: newTotal
        }
      };
    case 'SET_RECOMMENDATIONS':
      return { ...state, recommendations: action.payload };
    case 'SET_AGE_VERIFICATION':
      return { ...state, ageVerification: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'CLEAR_BASKET':
      return initialState;
    default:
      return state;
  }
}

const BasketContext = createContext<{
  state: BasketState;
  dispatch: React.Dispatch<BasketAction>;
} | null>(null);

export const BasketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(basketReducer, initialState);

  return (
    <BasketContext.Provider value={{ state, dispatch }}>
      {children}
    </BasketContext.Provider>
  );
};

export const useBasket = () => {
  const context = useContext(BasketContext);
  if (!context) {
    throw new Error('useBasket must be used within a BasketProvider');
  }
  return context;
};