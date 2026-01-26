import React, { useState } from 'react';
import { useQuery } from '@apollo/client';
import { Paper, Typography, Card, CardContent, Button, Chip, Box } from '@mui/material';
import { ShoppingCart, Warning } from '@mui/icons-material';
import { GET_PRODUCTS } from '../graphql/queries';
import { useProductAddition } from '../hooks/useProductAddition';

interface Product {
  productId: string;
  name: string;
  price: number;
  category: string;
  ageRestricted: boolean;
  minimumAge?: number;
}

const ProductList: React.FC = () => {
  const { data, loading, error } = useQuery(GET_PRODUCTS);
  const { addProduct } = useProductAddition();
  const [addingProduct, setAddingProduct] = useState<string | null>(null);

  const handleAddProduct = async (product: Product) => {
    setAddingProduct(product.productId);
    try {
      await addProduct({
        productId: product.productId,
        name: product.name,
        price: Number(product.price),
        quantity: 1
      });
    } finally {
      setAddingProduct(null);
    }
  };

  if (loading) return <div className="text-sm text-gray-500">Loading products...</div>;
  if (error) return <div className="text-sm text-red-500">Error loading products</div>;

  return (
    <Paper className="p-3">
      <Typography variant="subtitle1" className="mb-3 font-semibold">
        Products ({data?.products?.length || 0})
      </Typography>
      
      <Box className="grid grid-cols-2 gap-2 max-h-96 overflow-y-auto">
        {data?.products?.map((product: Product) => (
          <Card className="p-2" key={product.productId} variant="outlined">
            <Box className="space-y-1">
              <Box className="flex items-start justify-between">
                <Typography variant="caption" className="font-medium text-xs leading-tight">
                  {product.name}
                </Typography>
                {product.ageRestricted && (
                  <Chip
                    label={`${product.minimumAge}+`}
                    size="small"
                    color="warning"
                    className="h-4 text-xs ml-1"
                  />
                )}
              </Box>
              
              <Typography variant="caption" className="text-gray-500 text-xs">
                {product.category}
              </Typography>
              
              <Box className="flex justify-between items-center pt-1">
                <Typography variant="caption" className="font-bold text-green-600 text-xs">
                  ${Number(product.price).toFixed(2)}
                </Typography>
                
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<ShoppingCart />}
                  onClick={() => handleAddProduct(product)}
                  disabled={addingProduct === product.productId}
                  className="text-xs h-6 min-w-0 px-2"
                >
                  {addingProduct === product.productId ? '...' : '+'}
                </Button>
              </Box>
            </Box>
          </Card>
        ))}
      </Box>
    </Paper>
  );
};

export default ProductList;