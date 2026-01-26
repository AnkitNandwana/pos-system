from django.test import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from plugins.models import PluginConfiguration
from plugins.customer_lookup.plugin import CustomerLookupPlugin
from customers.models import Customer, CustomerLookupLog
from baskets.models import Basket
from employees.models import Employee


class CustomerLookupPluginTest(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.plugin_config = PluginConfiguration.objects.create(
            name='customer_lookup',
            enabled=True,
            config={
                'api_endpoint': 'http://localhost:8000/api/mock-customer-lookup/',
                'timeout_seconds': 5,
                'retry_attempts': 2,
                'cache_ttl_seconds': 3600,
                'fallback_to_cache_on_error': True
            }
        )
        
        self.plugin = CustomerLookupPlugin()
        
        # Create test employee and basket
        self.employee = Employee.objects.create_user(
            username='testuser',
            password='testpass123',
            employee_id='EMP001',
            first_name='Test',
            last_name='User',
            role='CASHIER'
        )
        
        self.basket = Basket.objects.create(
            basket_id='BASKET-123',
            employee=self.employee,
            status='ACTIVE'
        )
        
        self.event_data = {
            'basket_id': 'BASKET-123',
            'customer_identifier': 'phone:+1234567890'
        }
    
    def test_plugin_processes_events_when_enabled(self):
        """Test plugin processes basket.started events when enabled"""
        supported_events = self.plugin.get_supported_events()
        self.assertIn('basket.started', supported_events)
        
        with patch.object(self.plugin, '_handle_customer_lookup') as mock_handle:
            self.plugin.handle_event('basket.started', self.event_data)
            mock_handle.assert_called_once_with(self.event_data)
    
    def test_plugin_ignores_events_when_disabled(self):
        """Test plugin ignores events when disabled via registry"""
        # Disable plugin
        self.plugin_config.enabled = False
        self.plugin_config.save()
        
        # Test that disabled plugin is not returned by registry
        from plugins.registry import plugin_registry
        enabled_plugins = plugin_registry.get_enabled_plugins()
        plugin_names = [p.name for p in enabled_plugins]
        self.assertNotIn('customer_lookup', plugin_names)
    
    @patch('plugins.customer_lookup.plugin.CustomerAPIClient')
    @patch('plugins.customer_lookup.plugin.event_producer')
    def test_cache_hit_skips_api_call(self, mock_producer, mock_api_client):
        """Test cache hit skips external API call"""
        # Create cached customer
        customer = Customer.objects.create(
            customer_id='CUST-001',
            identifier='phone:+1234567890',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890',
            loyalty_points=100,
            tier='SILVER'
        )
        
        self.plugin.handle_event('basket.started', self.event_data)
        
        # API client should not be called
        mock_api_client.assert_not_called()
        
        # Basket should be updated with customer
        self.basket.refresh_from_db()
        self.assertEqual(self.basket.customer_id, 'CUST-001')
        
        # Lookup should be logged as success
        log = CustomerLookupLog.objects.get(basket_id='BASKET-123')
        self.assertEqual(log.status, 'SUCCESS')
    
    @patch('plugins.customer_lookup.plugin.CustomerAPIClient')
    @patch('plugins.customer_lookup.plugin.event_producer')
    def test_api_call_creates_customer(self, mock_producer, mock_api_client):
        """Test API call creates new customer"""
        # Mock API response
        api_data = {
            'customer_id': 'CUST-002',
            'identifier': 'phone:+1234567890',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone': '+1234567890',
            'loyalty_points': 250,
            'tier': 'GOLD',
            'total_purchases': 1500.00,
            'last_purchase_date': '2024-01-15T10:30:00Z'
        }
        
        mock_client_instance = Mock()
        mock_client_instance.fetch_customer.return_value = api_data
        mock_api_client.return_value = mock_client_instance
        
        self.plugin.handle_event('basket.started', self.event_data)
        
        # Customer should be created
        customer = Customer.objects.get(customer_id='CUST-002')
        self.assertEqual(customer.first_name, 'Jane')
        self.assertEqual(customer.last_name, 'Smith')
        self.assertEqual(customer.loyalty_points, 250)
        self.assertEqual(customer.tier, 'GOLD')
        
        # Basket should be updated
        self.basket.refresh_from_db()
        self.assertEqual(self.basket.customer_id, 'CUST-002')
        
        # Event should be published
        mock_producer.publish.assert_called_once()
    
    @patch('plugins.customer_lookup.plugin.CustomerAPIClient')
    @patch('plugins.customer_lookup.plugin.event_producer')
    def test_api_failure_with_cache_fallback(self, mock_producer, mock_api_client):
        """Test API failure falls back to cache when configured"""
        # Create stale cached customer
        customer = Customer.objects.create(
            customer_id='CUST-003',
            identifier='phone:+1234567890',
            first_name='Bob',
            last_name='Wilson',
            email='bob@example.com',
            phone='+1234567890',
            updated_at=timezone.now() - timedelta(hours=2)  # Stale cache
        )
        
        # Mock API failure
        mock_client_instance = Mock()
        mock_client_instance.fetch_customer.side_effect = Exception('API Error')
        mock_api_client.return_value = mock_client_instance
        
        self.plugin.handle_event('basket.started', self.event_data)
        
        # Should fall back to cached customer
        self.basket.refresh_from_db()
        self.assertEqual(self.basket.customer_id, 'CUST-003')
        
        # Lookup should be logged as failed initially, but fallback succeeds
        logs = CustomerLookupLog.objects.filter(basket_id='BASKET-123')
        self.assertTrue(logs.exists())
        # The plugin logs the API failure but then uses cache, so overall it's a success
    
    @patch('plugins.customer_lookup.plugin.CustomerAPIClient')
    @patch('plugins.customer_lookup.plugin.event_producer')
    def test_complete_lookup_workflow(self, mock_producer, mock_api_client):
        """Test complete customer lookup workflow"""
        # Mock successful API response
        api_data = {
            'customer_id': 'CUST-004',
            'identifier': 'email:test@example.com',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'email': 'test@example.com',
            'phone': '+9876543210',
            'loyalty_points': 500,
            'tier': 'PLATINUM',
            'total_purchases': 2500.50
        }
        
        mock_client_instance = Mock()
        mock_client_instance.fetch_customer.return_value = api_data
        mock_api_client.return_value = mock_client_instance
        
        event_data = {
            'basket_id': 'BASKET-123',
            'customer_identifier': 'email:test@example.com'
        }
        
        with patch('plugins.customer_lookup.plugin.event_producer') as mock_producer:
            self.plugin.handle_event('basket.started', event_data)
        
        # Verify customer created
        customer = Customer.objects.get(customer_id='CUST-004')
        self.assertEqual(customer.email, 'test@example.com')
        self.assertEqual(customer.tier, 'PLATINUM')
        self.assertEqual(customer.total_purchases, Decimal('2500.50'))
        
        # Verify basket updated
        self.basket.refresh_from_db()
        self.assertEqual(self.basket.customer_id, 'CUST-004')
        
        # Verify lookup logged
        log = CustomerLookupLog.objects.get(
            basket_id='BASKET-123',
            customer_identifier='email:test@example.com'
        )
        self.assertEqual(log.status, 'SUCCESS')
        self.assertIsNotNone(log.response_data)
        self.assertIsNotNone(log.duration_ms)
        
        # Verify event published
        mock_producer.publish.assert_called_once()
        published_data = mock_producer.publish.call_args[0][1]
        self.assertEqual(published_data['event_type'], 'CUSTOMER_DATA_FETCHED')
        self.assertEqual(published_data['customer_id'], 'CUST-004')