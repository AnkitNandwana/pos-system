import React from 'react';
import { Paper, Typography, Box, Chip } from '@mui/material';
import { Person, Star } from '@mui/icons-material';
import { Customer } from '../types';

interface CustomerInfoProps {
  customer: Customer | null;
}

const CustomerInfo: React.FC<CustomerInfoProps> = ({ customer }) => {
  if (!customer) {
    return (
      <Paper className="p-4">
        <Box className="flex items-center space-x-2 mb-2">
          <Person className="text-gray-400" />
          <Typography variant="h6">Guest Customer</Typography>
        </Box>
        <Typography variant="body2" className="text-gray-600">
          No customer information available
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper className="p-4">
      <Box className="flex items-center justify-between mb-3">
        <Box className="flex items-center space-x-2">
          <Person className="text-blue-600" />
          <Typography variant="h6">Customer Info</Typography>
        </Box>
        <Chip 
          icon={<Star />} 
          label={customer.tier} 
          color="primary" 
          size="small" 
        />
      </Box>
      
      <Box className="space-y-2">
        <Typography variant="body1" className="font-semibold">
          {customer.firstName} {customer.lastName}
        </Typography>
        <Typography variant="body2" className="text-gray-600">
          {customer.email}
        </Typography>
        <Typography variant="body2" className="text-gray-600">
          {customer.phone}
        </Typography>
        <Box className="flex justify-between items-center pt-2">
          <Typography variant="body2" className="text-gray-600">
            Loyalty Points:
          </Typography>
          <Typography variant="body2" className="font-semibold text-green-600">
            {customer.loyaltyPoints}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default CustomerInfo;