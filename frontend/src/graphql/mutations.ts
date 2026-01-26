import { gql } from '@apollo/client';

export const LOGIN_MUTATION = gql`
  mutation Login($username: String!, $password: String!) {
    login(username: $username, password: $password) {
      token
      employee {
        id
        username
        firstName
        lastName
        role
      }
      terminal {
        terminalId
        loginTime
        isActive
      }
    }
  }
`;

export const LOGOUT_MUTATION = gql`
  mutation Logout($terminalId: String!) {
    logout(terminalId: $terminalId) {
      success
      message
    }
  }
`;

export const START_BASKET_MUTATION = gql`
  mutation StartBasket($employeeId: Int!, $terminalId: String!, $customerIdentifier: String) {
    startBasket(employeeId: $employeeId, terminalId: $terminalId, customerIdentifier: $customerIdentifier) {
      basketId
      status
      customerId
      customer {
        customerId
        identifier
        firstName
        lastName
        email
        phone
        loyaltyPoints
        tier
      }
      items {
        id
        productId
        productName
        quantity
        price
      }
      totalAmount
      employee {
        id
        username
      }
    }
  }
`;

export const ADD_ITEM_MUTATION = gql`
  mutation AddItem($basketId: String!, $productId: String!, $productName: String!, $quantity: Int!, $price: Float!, $terminalId: String) {
    addItem(basketId: $basketId, productId: $productId, productName: $productName, quantity: $quantity, price: $price, terminalId: $terminalId) {
      id
      productId
      productName
      quantity
      price
    }
  }
`;

export const REMOVE_ITEM_MUTATION = gql`
  mutation RemoveItem($basketId: String!, $itemId: String!) {
    removeItem(basketId: $basketId, itemId: $itemId)
  }
`;

export const UPDATE_QUANTITY_MUTATION = gql`
  mutation UpdateQuantity($basketId: String!, $itemId: String!, $quantity: Int!) {
    updateQuantity(basketId: $basketId, itemId: $itemId, quantity: $quantity) {
      id
      quantity
    }
  }
`;

export const ACCEPT_RECOMMENDATION_MUTATION = gql`
  mutation AcceptRecommendation($recommendationId: Int!) {
    acceptRecommendation(recommendationId: $recommendationId) {
      id
      status
    }
  }
`;

export const REJECT_RECOMMENDATION_MUTATION = gql`
  mutation RejectRecommendation($recommendationId: Int!) {
    rejectRecommendation(recommendationId: $recommendationId) {
      id
      status
    }
  }
`;

export const UPDATE_PLUGIN_MUTATION = gql`
  mutation UpdatePlugin($id: ID!, $enabled: Boolean, $config: String, $supportedEvents: [String!]) {
    updatePlugin(id: $id, enabled: $enabled, config: $config, supportedEvents: $supportedEvents) {
      id
      name
      enabled
      description
      config
      supportedEvents
    }
  }
`;

export const VERIFY_AGE_MUTATION = gql`
  mutation VerifyAge($basketId: String!, $verifierEmployeeId: Int!, $customerAge: Int!, $verificationMethod: String) {
    verifyAge(basketId: $basketId, verifierEmployeeId: $verifierEmployeeId, customerAge: $customerAge, verificationMethod: $verificationMethod)
  }
`;

export const CANCEL_AGE_VERIFICATION_MUTATION = gql`
  mutation CancelAgeVerification($basketId: String!, $employeeId: Int!) {
    cancelAgeVerification(basketId: $basketId, employeeId: $employeeId)
  }
`;

export const ADD_VERIFIED_ITEM_MUTATION = gql`
  mutation AddVerifiedItem($basketId: String!, $productId: String!, $productName: String!, $quantity: Int!, $price: Float!) {
    addVerifiedItem(basketId: $basketId, productId: $productId, productName: $productName, quantity: $quantity, price: $price) {
      id
      productId
      productName
      quantity
      price
    }
  }
`;

export const PROCESS_PAYMENT_MUTATION = gql`
  mutation ProcessPayment($basketId: String!, $terminalId: String!, $employeeId: Int!, $totalAmount: Float!, $paymentMethod: String!) {
    processPayment(basketId: $basketId, terminalId: $terminalId, employeeId: $employeeId, totalAmount: $totalAmount, paymentMethod: $paymentMethod)
  }
`;