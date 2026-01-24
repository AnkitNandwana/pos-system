from django.http import JsonResponse
from django.views import View
import json


class MockCustomerLookupView(View):
    """Mock external API for customer lookup"""
    
    MOCK_CUSTOMERS = {
        '+1234567890': {
            'customer_id': 'CUST_001',
            'identifier': '+1234567890',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'loyalty_points': 1250,
            'tier': 'GOLD',
            'total_purchases': 5432.50,
            'last_purchase_date': '2024-01-10T15:30:00Z'
        },
        '+0987654321': {
            'customer_id': 'CUST_002',
            'identifier': '+0987654321',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '+0987654321',
            'loyalty_points': 5000,
            'tier': 'PLATINUM',
            'total_purchases': 12500.00,
            'last_purchase_date': '2024-01-12T10:00:00Z'
        },
        'john@example.com': {
            'customer_id': 'CUST_001',
            'identifier': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'loyalty_points': 1250,
            'tier': 'GOLD',
            'total_purchases': 5432.50,
            'last_purchase_date': '2024-01-10T15:30:00Z'
        },
        'CARD_123456': {
            'customer_id': 'CUST_003',
            'identifier': 'CARD_123456',
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'email': 'bob.wilson@example.com',
            'phone': '+1122334455',
            'loyalty_points': 500,
            'tier': 'SILVER',
            'total_purchases': 1200.00,
            'last_purchase_date': '2024-01-08T14:20:00Z'
        },
        '+5555555555': {
            'customer_id': 'CUST_004',
            'identifier': '+5555555555',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'email': 'alice.j@example.com',
            'phone': '+5555555555',
            'loyalty_points': 250,
            'tier': 'BRONZE',
            'total_purchases': 450.00,
            'last_purchase_date': '2024-01-05T09:15:00Z'
        }
    }
    
    def get(self, request, identifier):
        """Lookup customer by identifier"""
        customer_data = self.MOCK_CUSTOMERS.get(identifier)
        
        if customer_data:
            return JsonResponse(customer_data)
        else:
            return JsonResponse({
                'error': 'Customer not found'
            }, status=404)
