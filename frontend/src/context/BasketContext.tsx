import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Basket, Customer, BasketItem, AgeVerificationState, Recommendation, RestrictedItem } from '../types';

interface BasketState {
  basket: Basket | null;
  customer: Customer | null;
  ageVerification: AgeVerificationState;
  recommendations: Recommendation[];
  loading: boolean;
  error: string | null;
  pluginStatus: { [key: string]: boolean };
  verificationState: 'idle' | 'pending' | 'required' | 'verifying' | 'verified' | 'failed';
  pendingItems: RestrictedItem[];
  paymentState: 'idle' | 'processing' | 'completed' | 'failed';
  showPaymentModal: boolean;
  showThankYou: boolean;
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
  | { type: 'CLEAR_BASKET' }
  | { type: 'SET_PLUGIN_STATUS'; payload: { [key: string]: boolean } }
  | { type: 'SET_VERIFICATION_STATE'; payload: 'idle' | 'pending' | 'required' | 'verifying' | 'verified' | 'failed' }
  | { type: 'SET_PENDING_ITEMS'; payload: RestrictedItem[] }
  | { type: 'CLEAR_PENDING_ITEMS' }
  | { type: 'AGE_VERIFICATION_REQUIRED'; payload: { restrictedItems: RestrictedItem[]; minimumAge: number } }
  | { type: 'AGE_VERIFICATION_COMPLETED'; payload: { customerAge: number; verificationMethod: string } }
  | { type: 'AGE_VERIFICATION_FAILED'; payload: { reason: string } }
  | { type: 'SET_PAYMENT_STATE'; payload: 'idle' | 'processing' | 'completed' | 'failed' }
  | { type: 'SHOW_PAYMENT_MODAL'; payload: boolean }
  | { type: 'SHOW_THANK_YOU'; payload: boolean };

const initialState: BasketState = {
  basket: null,
  customer: null,
  ageVerification: { required: false, verified: false },
  recommendations: [],
  loading: false,
  error: null,
  pluginStatus: {},
  verificationState: 'idle',
  pendingItems: [],
  paymentState: 'idle',
  showPaymentModal: false,
  showThankYou: false,
};

function basketReducer(state: BasketState, action: BasketAction): BasketState {
  switch (action.type) {
    case 'SET_BASKET':
      return { ...state, basket: action.payload };
    case 'SET_CUSTOMER':
      return { ...state, customer: action.payload };
    case 'ADD_ITEM':
      if (!state.basket) return state;
      
      // Check if item already exists
      const existingItemIndex = state.basket.items.findIndex(
        item => item.productId === action.payload.productId
      );
      
      if (existingItemIndex >= 0) {
        // Replace existing item with backend response (backend handles quantity increment)
        const updatedItems = [...state.basket.items];
        const oldQuantity = updatedItems[existingItemIndex].quantity;
        updatedItems[existingItemIndex] = action.payload;
        
        return {
          ...state,
          basket: {
            ...state.basket,
            items: updatedItems,
            totalAmount: state.basket.totalAmount - (updatedItems[existingItemIndex].price * oldQuantity) + (action.payload.price * action.payload.quantity)
          }
        };
      } else {
        // Add new item
        return {
          ...state,
          basket: {
            ...state.basket,
            items: [...state.basket.items, action.payload],
            totalAmount: state.basket.totalAmount + (action.payload.price * action.payload.quantity)
          }
        };
      }
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
    case 'SET_PLUGIN_STATUS':
      return { ...state, pluginStatus: action.payload };
    case 'SET_VERIFICATION_STATE':
      return { ...state, verificationState: action.payload };
    case 'SET_PENDING_ITEMS':
      return { ...state, pendingItems: action.payload };
    case 'CLEAR_PENDING_ITEMS':
      return { ...state, pendingItems: [], verificationState: 'idle' };
    case 'AGE_VERIFICATION_REQUIRED':
      return {
        ...state,
        ageVerification: {
          required: true,
          verified: false,
          restrictedItems: action.payload.restrictedItems,
          minimumAge: action.payload.minimumAge
        }
      };
    case 'AGE_VERIFICATION_COMPLETED':
      return {
        ...state,
        ageVerification: {
          ...state.ageVerification,
          verified: true,
          customerAge: action.payload.customerAge,
          verificationMethod: action.payload.verificationMethod
        }
      };
    case 'AGE_VERIFICATION_FAILED':
      return {
        ...state,
        ageVerification: {
          ...state.ageVerification,
          verified: false
        },
        error: action.payload.reason
      };
    case 'SET_PAYMENT_STATE':
      return { ...state, paymentState: action.payload };
    case 'SHOW_PAYMENT_MODAL':
      return { ...state, showPaymentModal: action.payload };
    case 'SHOW_THANK_YOU':
      return { ...state, showThankYou: action.payload };
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