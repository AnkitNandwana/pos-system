import React, { useState } from 'react';
import { useLazyQuery } from '@apollo/client';
import {
  Paper,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Box,
  Chip
} from '@mui/material';
import { Add, Search } from '@mui/icons-material';
import { SEARCH_PRODUCTS } from '../graphql/queries';
import { useBasket } from '../context/BasketContext';
import { useProductAddition } from '../hooks/useProductAddition';
import { Product } from '../types';

interface SearchProductsData {
  searchProducts: Product[];
}

const ProductSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const { state } = useBasket();
  const { addProduct } = useProductAddition();
  
  const [searchProducts, { data, loading }] = useLazyQuery<SearchProductsData>(SEARCH_PRODUCTS);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.length > 2) {
      searchProducts({ variables: { query } });
    }
  };

  const handleAddItem = (product: Product) => {
    if (!state.basket) return;
    
    addProduct({
      productId: product.productId,
      name: product.name,
      price: parseFloat(product.price.toString()),
      quantity: 1
    });
  };

  return (
    <Paper className="p-4">
      <Typography variant="h6" className="mb-3">
        Add Products
      </Typography>
      
      <TextField
        fullWidth
        placeholder="Search products..."
        value={searchQuery}
        onChange={(e) => handleSearch(e.target.value)}
        InputProps={{
          startAdornment: <Search className="mr-2 text-gray-400" />
        }}
        className="mb-3"
      />

      {data?.searchProducts && (
        <List>
          {data.searchProducts.map((product: Product) => (
            <ListItem key={product.productId} divider>
              <ListItemText
                primary={
                  <Box className="flex items-center space-x-2">
                    <span>{product.name}</span>
                    {product.ageRestricted && (
                      <Chip size="small" label={`${product.minimumAge}+`} color="warning" />
                    )}
                  </Box>
                }
                secondary={`$${product.price} • ${product.category}`}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => handleAddItem(product)}
                  color="primary"
                  disabled={state.verificationState === 'pending' || state.verificationState === 'verifying'}
                >
                  <Add />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default ProductSearch;