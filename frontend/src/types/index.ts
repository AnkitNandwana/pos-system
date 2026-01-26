export interface Employee {
  id: number;
  username: string;
  firstName: string;
  lastName: string;
  role: string;
}

export interface Terminal {
  terminalId: string;
  loginTime: string;
  isActive: boolean;
}

export interface Customer {
  customerId: string;
  identifier: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  loyaltyPoints: number;
  tier: string;
}

export interface Product {
  productId: string;
  name: string;
  price: number;
  category: string;
  ageRestricted: boolean;
  minimumAge?: number;
}

export interface BasketItem {
  id: string;
  productId: string;
  productName: string;
  quantity: number;
  price: number;
}

export interface Basket {
  basketId: string;
  status: string;
  customerId?: string;
  customer?: Customer;
  items: BasketItem[];
  totalAmount: number;
  employee: {
    id: number;
    username: string;
  };
}

export interface Recommendation {
  id: number;
  recommendedProductId: string;
  recommendedProductName: string;
  recommendedPrice: number;
  reason: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
}

export interface AgeVerificationState {
  required: boolean;
  verified: boolean;
  productId?: string;
  minimumAge?: number;
  restrictedItems?: RestrictedItem[];
  customerAge?: number;
  verificationMethod?: string;
}

export interface RestrictedItem {
  productId: string;
  name: string;
  minimumAge?: number;
  minimum_age?: number;  // Backend sends snake_case
  category: string;
  quantity?: number;
  price?: number;
}

export interface Plugin {
  id: string;
  name: string;
  enabled: boolean;
  description: string;
  config: string;
  supportedEvents: string[];
}

export interface LoginResponse {
  token: string;
  employee: Employee;
  terminal: Terminal;
}

export interface LogoutResponse {
  success: boolean;
  message: string;
}