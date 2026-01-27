import React from 'react';
import { useMutation } from '@apollo/client';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip
} from '@mui/material';
import { Add } from '@mui/icons-material';
import { ADD_ITEM_MUTATION } from '../graphql/mutations';
import { useBasket } from '../context/BasketContext';
import { Recommendation } from '../types';

interface RecommendationPanelProps {
  recommendations: Recommendation[];
}

const RecommendationPanel: React.FC<RecommendationPanelProps> = ({ recommendations }) => {
  const { state, dispatch } = useBasket();
  
  // Filter unique recommendations by product ID
  const uniqueRecommendations = recommendations.reduce((unique: Recommendation[], rec) => {
    const exists = unique.find(item => item.recommendedProductId === rec.recommendedProductId);
    if (!exists) {
      unique.push(rec);
    }
    return unique;
  }, []);
  
  const [addItem] = useMutation(ADD_ITEM_MUTATION, {
    onCompleted: (data: any) => {
      dispatch({ type: 'ADD_ITEM', payload: data.addItem });
    }
  });

  const handleAddRecommendation = (rec: Recommendation) => {
    if (!state.basket) return;
    
    addItem({
      variables: {
        basketId: state.basket.basketId,
        productId: rec.recommendedProductId,
        productName: rec.recommendedProductName,
        quantity: 1,
        price: parseFloat(rec.recommendedPrice.toString())
      }
    });
    
    // Remove all recommendations for this product immediately
    const updatedRecommendations = recommendations.filter(r => r.recommendedProductId !== rec.recommendedProductId);
    dispatch({ type: 'SET_RECOMMENDATIONS', payload: updatedRecommendations });
  };

  return (
    <Paper className="p-4">
      <Typography variant="h6" className="mb-3 text-green-600">
        Recommended for You
      </Typography>
      
      <List>
        {uniqueRecommendations.map((rec) => (
          <ListItem key={rec.recommendedProductId} divider>
            <ListItemText
              primary={rec.recommendedProductName}
              secondary={
                <div>
                  <div>${rec.recommendedPrice}</div>
                  <Chip size="small" label={rec.reason} variant="outlined" />
                </div>
              }
            />
            <ListItemSecondaryAction>
              <IconButton
                edge="end"
                onClick={() => handleAddRecommendation(rec)}
                color="primary"
              >
                <Add />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default RecommendationPanel;