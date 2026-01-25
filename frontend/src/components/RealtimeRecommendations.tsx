import React, { useEffect, useState } from 'react';
import { useMutation } from '@apollo/client/react';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Button,
  Box,
  Chip,
  Alert
} from '@mui/material';
import { CheckCircle, Cancel, Lightbulb } from '@mui/icons-material';
import { ACCEPT_RECOMMENDATION_MUTATION, REJECT_RECOMMENDATION_MUTATION } from '../graphql/mutations';
import { useBasket } from '../context/BasketContext';
import { Recommendation } from '../types';

const RealtimeRecommendations: React.FC = () => {
  const { state, dispatch } = useBasket();
  const { basket } = state;
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [connected, setConnected] = useState(false);

  const [acceptRecommendation] = useMutation(ACCEPT_RECOMMENDATION_MUTATION);
  const [rejectRecommendation] = useMutation(REJECT_RECOMMENDATION_MUTATION);

  useEffect(() => {
    if (!basket?.basketId) return;

    const eventSource = new EventSource(`http://localhost:8000/events/recommendations/${basket.basketId}/`);
    
    eventSource.onopen = () => {
      console.log('SSE connected');
      setConnected(true);
    };
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received recommendations:', data);
      
      if (data.type === 'recommendations') {
        const formattedRecs = data.recommendations.map((rec: any) => ({
          id: rec.id,
          recommendedProductId: rec.recommended_product_id,
          recommendedProductName: rec.recommended_product_name,
          recommendedPrice: rec.recommended_price,
          reason: rec.reason,
          status: rec.status
        }));
        setRecommendations(formattedRecs);
        dispatch({ type: 'SET_RECOMMENDATIONS', payload: formattedRecs });
      }
    };
    
    eventSource.onerror = () => {
      console.log('SSE error');
      setConnected(false);
    };

    return () => {
      eventSource.close();
    };
  }, [basket?.basketId, dispatch]);

  const handleAccept = (recommendation: Recommendation) => {
    acceptRecommendation({
      variables: { recommendationId: recommendation.id }
    }).then(() => {
      // Remove accepted recommendation from local state
      setRecommendations(prev => prev.filter(r => r.id !== recommendation.id));
      
      // Add item to basket context
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
    });
  };

  const handleReject = (recommendation: Recommendation) => {
    rejectRecommendation({
      variables: { recommendationId: recommendation.id }
    }).then(() => {
      // Remove rejected recommendation from local state
      setRecommendations(prev => prev.filter(r => r.id !== recommendation.id));
    });
  };

  if (!basket) {
    return null;
  }

  if (!connected) {
    return (
      <Paper className="p-4 border-l-4 border-gray-300">
        <Typography variant="body2" className="text-gray-500">
          Connecting to real-time recommendations...
        </Typography>
      </Paper>
    );
  }

  if (!recommendations.length) {
    return (
      <Paper className="p-4 border-l-4 border-gray-300">
        <Typography variant="body2" className="text-gray-500">
          No recommendations available (Basket: {basket.basketId})
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper className="p-4 border-l-4 border-orange-500">
      <Box className="flex items-center space-x-2 mb-3">
        <Lightbulb className="text-orange-500" />
        <Typography variant="h6" className="text-orange-600">
          Smart Recommendations
        </Typography>
        <Chip size="small" label="Real-time" color="success" />
      </Box>
      
      <Alert severity="info" className="mb-3">
        Based on your current items, we suggest:
      </Alert>
      
      <List>
        {recommendations.map((rec) => (
          <ListItem key={rec.id} divider className="bg-orange-50">
            <ListItemText
              primary={
                <Box className="flex items-center space-x-2">
                  <span className="font-semibold">{rec.recommendedProductName}</span>
                  <Chip size="small" label={`$${rec.recommendedPrice}`} variant="outlined" />
                </Box>
              }
              secondary={
                <Box className="mt-1">
                  <Typography variant="body2" className="text-gray-600">
                    {rec.reason}
                  </Typography>
                </Box>
              }
            />
            <ListItemSecondaryAction>
              <Box className="flex space-x-2">
                <Button
                  size="small"
                  variant="contained"
                  color="success"
                  startIcon={<CheckCircle />}
                  onClick={() => handleAccept(rec)}
                >
                  Add
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  color="error"
                  startIcon={<Cancel />}
                  onClick={() => handleReject(rec)}
                >
                  Skip
                </Button>
              </Box>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default RealtimeRecommendations;