import { gql } from '@apollo/client';

export const GET_PLUGINS = gql`
  query GetPlugins {
    plugins {
      id
      name
      enabled
      description
      config
      supportedEvents
    }
  }
`;

export const SEARCH_PRODUCTS = gql`
  query SearchProducts($query: String!) {
    searchProducts(query: $query) {
      productId
      name
      price
      category
      ageRestricted
      minimumAge
    }
  }
`;

export const GET_BASKET_DETAILS = gql`
  query GetBasketDetails($basketId: String!) {
    basketDetails(basketId: $basketId) {
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
      employee {
        id
        username
      }
      items {
        id
        productId
        productName
        quantity
        price
      }
      totalAmount
    }
  }
`;

export const GET_RECOMMENDATIONS = gql`
  query GetRecommendations($basketId: String!) {
    pendingRecommendations(basketId: $basketId) {
      id
      recommendedProductId
      recommendedProductName
      recommendedPrice
      reason
      status
    }
  }
`;

export const ACCEPT_RECOMMENDATION = gql`
  mutation AcceptRecommendation($recommendationId: Int!, $basketId: String!) {
    acceptRecommendation(recommendationId: $recommendationId, basketId: $basketId) {
      success
      message
    }
  }
`;

export const REJECT_RECOMMENDATION = gql`
  mutation RejectRecommendation($recommendationId: Int!) {
    rejectRecommendation(recommendationId: $recommendationId) {
      success
      message
    }
  }
`;