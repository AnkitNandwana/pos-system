import React, { useState, useEffect } from 'react';
import { useMutation } from '@apollo/client';
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
import { ACCEPT_RECOMMENDATION, REJECT_RECOMMENDATION } from '../graphql/queries';
import { ADD_ITEM_MUTATION } from '../graphql/mutations';
import { useBasket } from '../context/BasketContext';
import { Recommendation } from '../types';

const RealtimeRecommendations: React.FC = () => {
  const { state, dispatch } = useBasket();
  const { basket } = state;
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!basket?.basketId) return;

    console.log(`Connecting to WebSocket: ws://localhost:8000/ws/recommendations/${basket.basketId}/`);
    const ws = new WebSocket(`ws://localhost:8000/ws/recommendations/${basket.basketId}/`);
    
    ws.onopen = () => {
      console.log('WebSocket connected for basket:', basket.basketId);
      setConnected(true);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received WebSocket message:', data);
      
      if (data.type === 'test') {
        console.log('Test message received:', data.message);
      } else if (data.type === 'recommendations') {
        console.log('Setting recommendations:', data.recommendations);
        setRecommendations(data.recommendations);
        dispatch({ type: 'SET_RECOMMENDATIONS', payload: data.recommendations });
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      setConnected(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        console.log('Closing WebSocket connection');
        ws.close();
      }
    };
  }, [basket?.basketId, dispatch]);

  const [acceptRecommendation] = useMutation(ACCEPT_RECOMMENDATION);
  const [rejectRecommendation] = useMutation(REJECT_RECOMMENDATION);
  const [addItem] = useMutation(ADD_ITEM_MUTATION);

  const handleAccept = async (recommendation: Recommendation) => {
    try {
      // Remove all recommendations for this product immediately for better UX
      setRecommendations(prev => prev.filter(r => r.recommendedProductId !== recommendation.recommendedProductId));
      
      const result = await acceptRecommendation({
        variables: {
          recommendationId: recommendation.id,
          basketId: basket?.basketId
        }
      });
      
      if (result.data?.acceptRecommendation?.success) {
        // Add item to database via GraphQL
        const addResult = await addItem({
          variables: {
            basketId: basket?.basketId,
            productId: recommendation.recommendedProductId,
            productName: recommendation.recommendedProductName,
            quantity: 1,
            price: recommendation.recommendedPrice
          }
        });
        
        // Add to context with the actual database ID
        if (addResult.data?.addItem) {
          dispatch({
            type: 'ADD_ITEM',
            payload: addResult.data.addItem
          });
        }
      }
    } catch (error) {
      console.error('Error accepting recommendation:', error);
    }
  };

  const handleReject = async (recommendation: Recommendation) => {
    try {
      // Remove all recommendations for this product immediately for better UX
      setRecommendations(prev => prev.filter(r => r.recommendedProductId !== recommendation.recommendedProductId));
      
      await rejectRecommendation({
        variables: { recommendationId: recommendation.id }
      });
    } catch (error) {
      console.error('Error rejecting recommendation:', error);
    }
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

  // Filter unique recommendations by product ID
  const uniqueRecommendations = recommendations.reduce((unique: Recommendation[], rec) => {
    const exists = unique.find(item => item.recommendedProductId === rec.recommendedProductId);
    if (!exists) {
      unique.push(rec);
    }
    return unique;
  }, []);

  if (!uniqueRecommendations.length) {
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
        {uniqueRecommendations.map((rec) => (
          <ListItem key={rec.recommendedProductId} divider className="bg-orange-50">
            <ListItemText
              primary={
                <Box className="flex items-center space-x-2">
                  <span className="font-semibold">{rec.recommendedProductName}</span>
                  <Chip size="small" label={`$${rec.recommendedPrice}`} variant="outlined" />
                </Box>
              }
              secondary={
                <Typography variant="body2" className="text-gray-600">
                  {rec.reason}
                </Typography>
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