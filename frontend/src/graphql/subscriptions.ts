import { gql } from '@apollo/client';

export const RECOMMENDATIONS_SUBSCRIPTION = gql`
  subscription RecommendationsSubscription($basketId: String!) {
    recommendations(basketId: $basketId) {
      id
      recommendedProductId
      recommendedProductName
      recommendedPrice
      reason
      status
    }
  }
`;

export const AGE_VERIFICATION_SUBSCRIPTION = gql`
  subscription AgeVerificationEvents($basketId: String!) {
    ageVerificationEvents(basketId: $basketId) {
      eventType
      basketId
      restrictedItems {
        productId
        name
        minimumAge
        category
      }
      minimumAge
      customerAge
      verificationMethod
      verifierId
      reason
      actionRequired
    }
  }
`;