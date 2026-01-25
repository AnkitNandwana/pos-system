import React from 'react';
import { useSubscription, useMutation } from '@apollo/client';
import { RECOMMENDATIONS_SUBSCRIPTION } from '../graphql/subscriptions';
import { ACCEPT_RECOMMENDATION, REJECT_RECOMMENDATION } from '../graphql/queries';
import { Recommendation } from '../types';
import { useBasket } from '../context/BasketContext';

interface RecommendationsProps {
  basketId: string;
}

const Recommendations: React.FC<RecommendationsProps> = ({ basketId }) => {
  const { dispatch } = useBasket();
  
  const { data, loading, error } = useSubscription(RECOMMENDATIONS_SUBSCRIPTION, {
    variables: { basketId },
    onData: ({ data }: any) => {
      if (data?.data?.recommendations) {
        dispatch({ 
          type: 'SET_RECOMMENDATIONS', 
          payload: data.data.recommendations 
        });
      }
    }
  });

  const [acceptRecommendation] = useMutation(ACCEPT_RECOMMENDATION);
  const [rejectRecommendation] = useMutation(REJECT_RECOMMENDATION);

  const handleAccept = async (recommendation: Recommendation) => {
    try {
      const result = await acceptRecommendation({
        variables: {
          recommendationId: recommendation.id,
          basketId
        }
      });
      
      if (result.data?.acceptRecommendation?.success) {
        // Add item to basket
        dispatch({
          type: 'ADD_ITEM',
          payload: {
            id: `rec_${recommendation.id}`,
            productId: recommendation.recommendedProductId,
            productName: recommendation.recommendedProductName,
            quantity: 1,
            price: recommendation.recommendedPrice
          }
        });
        
        // Remove from recommendations
        dispatch({
          type: 'SET_RECOMMENDATIONS',
          payload: data?.recommendations?.filter((r: Recommendation) => r.id !== recommendation.id) || []
        });
      }
    } catch (error) {
      console.error('Error accepting recommendation:', error);
    }
  };

  const handleReject = async (recommendation: Recommendation) => {
    try {
      await rejectRecommendation({
        variables: { recommendationId: recommendation.id }
      });
      
      // Remove from recommendations
      dispatch({
        type: 'SET_RECOMMENDATIONS',
        payload: data?.recommendations?.filter((r: Recommendation) => r.id !== recommendation.id) || []
      });
    } catch (error) {
      console.error('Error rejecting recommendation:', error);
    }
  };

  if (loading) return <div>Loading recommendations...</div>;
  if (error) return <div>Error loading recommendations: {error.message}</div>;
  if (!data?.recommendations?.length) return null;

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
      <h3 className="text-lg font-semibold text-blue-800 mb-3">
        Recommended Items
      </h3>
      <div className="space-y-2">
        {data.recommendations.map((recommendation: Recommendation) => (
          <div key={recommendation.id} className="flex items-center justify-between bg-white p-3 rounded border">
            <div className="flex-1">
              <div className="font-medium">{recommendation.recommendedProductName}</div>
              <div className="text-sm text-gray-600">${recommendation.recommendedPrice.toFixed(2)}</div>
              <div className="text-xs text-gray-500">{recommendation.reason}</div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handleAccept(recommendation)}
                className="px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600"
              >
                Add
              </button>
              <button
                onClick={() => handleReject(recommendation)}
                className="px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600"
              >
                Dismiss
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Recommendations;