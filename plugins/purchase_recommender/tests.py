from django.test import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal
from django.utils import timezone

from plugins.models import PluginConfiguration
from plugins.purchase_recommender.plugin import PurchaseRecommenderPlugin
from plugins.purchase_recommender.models import Recommendation
from products.models import Product, RecommendationRule
from baskets.models import Basket
from employees.models import Employee


class PurchaseRecommenderPluginTest(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.plugin_config = PluginConfiguration.objects.create(
            name='purchase_recommender',
            enabled=True,
            config={}
        )
        
        self.plugin = PurchaseRecommenderPlugin()
        
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
        
        # Create test products
        self.burger = Product.objects.create(
            product_id='BURGER',
            name='Hamburger',
            price=Decimal('8.99'),
            category='Food'
        )
        
        self.fries = Product.objects.create(
            product_id='FRIES',
            name='French Fries',
            price=Decimal('2.99'),
            category='Food'
        )
        
        self.coke = Product.objects.create(
            product_id='COKE',
            name='Coca Cola',
            price=Decimal('1.99'),
            category='Beverage'
        )
        
        self.event_data = {
            'basket_id': 'BASKET-123',
            'product_id': 'BURGER'
        }
    
    def test_plugin_processes_events_when_enabled(self):
        """Test plugin processes item.added events when enabled"""
        supported_events = self.plugin.get_supported_events()
        self.assertIn('item.added', supported_events)
        
        with patch.object(self.plugin, '_handle_item_added') as mock_handle:
            self.plugin.handle_event('item.added', self.event_data)
            mock_handle.assert_called_once_with(self.event_data)
    
    def test_plugin_ignores_events_when_disabled(self):
        """Test plugin ignores events when disabled"""
        self.plugin_config.enabled = False
        self.plugin_config.save()
        
        with patch.object(self.plugin, '_handle_item_added') as mock_handle:
            self.plugin.handle_event('item.added', self.event_data)
            mock_handle.assert_not_called()
    
    @patch('plugins.purchase_recommender.plugin.event_producer')
    @patch('plugins.purchase_recommender.plugin.async_to_sync')
    def test_hardcoded_recommendations_created(self, mock_async, mock_producer):
        """Test hardcoded recommendations are created for known products"""
        self.plugin.handle_event('item.added', self.event_data)
        
        # Should create recommendations based on hardcoded rules
        recommendations = Recommendation.objects.filter(basket_id='BASKET-123')
        self.assertEqual(recommendations.count(), 2)
        
        # Check specific recommendations
        fries_rec = recommendations.get(recommended_product_id='FRIES')
        self.assertEqual(fries_rec.source_product_id, 'BURGER')
        self.assertEqual(fries_rec.recommended_product_name, 'French Fries')
        self.assertEqual(fries_rec.recommended_price, Decimal('2.99'))
        self.assertEqual(fries_rec.status, 'PENDING')
        
        coke_rec = recommendations.get(recommended_product_id='COKE')
        self.assertEqual(coke_rec.source_product_id, 'BURGER')
        self.assertEqual(coke_rec.recommended_product_name, 'Coca Cola')
        self.assertEqual(coke_rec.recommended_price, Decimal('1.99'))
        
        # Event should be published
        mock_producer.publish.assert_called_once()
    
    @patch('plugins.purchase_recommender.plugin.event_producer')
    @patch('plugins.purchase_recommender.plugin.async_to_sync')
    def test_database_rules_override_hardcoded(self, mock_async, mock_producer):
        """Test database rules take precedence over hardcoded rules"""
        # Create database recommendation rule
        RecommendationRule.objects.create(
            source_product=self.burger,
            recommended_product=self.fries,
            priority=1,
            is_active=True
        )
        
        self.plugin.handle_event('item.added', self.event_data)
        
        # Should create only one recommendation from database rule
        recommendations = Recommendation.objects.filter(basket_id='BASKET-123')
        self.assertEqual(recommendations.count(), 1)
        
        rec = recommendations.first()
        self.assertEqual(rec.recommended_product_id, 'FRIES')
        self.assertEqual(rec.recommended_product_name, 'French Fries')
        self.assertEqual(rec.recommended_price, Decimal('2.99'))
    
    @patch('plugins.purchase_recommender.plugin.event_producer')
    @patch('plugins.purchase_recommender.plugin.async_to_sync')
    def test_no_recommendations_for_unknown_product(self, mock_async, mock_producer):
        """Test no recommendations created for unknown products"""
        event_data = {
            'basket_id': 'BASKET-123',
            'product_id': 'UNKNOWN_PRODUCT'
        }
        
        self.plugin.handle_event('item.added', event_data)
        
        # Should not create any recommendations
        recommendations = Recommendation.objects.filter(basket_id='BASKET-123')
        self.assertEqual(recommendations.count(), 0)
        
        # Event should not be published
        mock_producer.publish.assert_not_called()
    
    @patch('plugins.purchase_recommender.plugin.event_producer')
    @patch('plugins.purchase_recommender.plugin.async_to_sync')
    def test_websocket_message_sent(self, mock_async, mock_producer):
        """Test WebSocket message is sent with recommendations"""
        mock_channel_layer = Mock()
        mock_group_send = Mock()
        mock_async.return_value = mock_group_send
        
        with patch('plugins.purchase_recommender.plugin.get_channel_layer', return_value=mock_channel_layer):
            self.plugin.handle_event('item.added', self.event_data)
        
        # WebSocket message should be sent
        mock_async.assert_called_once()
        mock_group_send.assert_called_once_with(
            f'recommendations_BASKET-123',
            {
                'type': 'recommendation_message',
                'recommendations': [
                    {
                        'id': 0,
                        'recommendedProductId': 'FRIES',
                        'recommendedProductName': 'French Fries',
                        'recommendedPrice': 2.99,
                        'reason': 'Frequently bought together',
                        'status': 'PENDING'
                    },
                    {
                        'id': 0,
                        'recommendedProductId': 'COKE',
                        'recommendedProductName': 'Coca Cola',
                        'recommendedPrice': 1.99,
                        'reason': 'Frequently bought together',
                        'status': 'PENDING'
                    }
                ]
            }
        )
    
    @patch('plugins.purchase_recommender.plugin.event_producer')
    @patch('plugins.purchase_recommender.plugin.async_to_sync')
    def test_complete_recommendation_workflow(self, mock_async, mock_producer):
        """Test complete recommendation workflow"""
        # Test with COFFEE product (different hardcoded rules)
        event_data = {
            'basket_id': 'BASKET-456',
            'product_id': 'COFFEE'
        }
        
        self.plugin.handle_event('item.added', event_data)
        
        # Verify recommendations created
        recommendations = Recommendation.objects.filter(basket_id='BASKET-456')
        self.assertEqual(recommendations.count(), 2)
        
        # Check specific recommendations
        donut_rec = recommendations.get(recommended_product_id='DONUT')
        self.assertEqual(donut_rec.source_product_id, 'COFFEE')
        self.assertEqual(donut_rec.recommended_product_name, 'Donut')
        self.assertEqual(donut_rec.recommended_price, Decimal('1.99'))
        self.assertEqual(donut_rec.reason, 'Frequently bought together')
        self.assertEqual(donut_rec.status, 'PENDING')
        
        muffin_rec = recommendations.get(recommended_product_id='MUFFIN')
        self.assertEqual(muffin_rec.source_product_id, 'COFFEE')
        self.assertEqual(muffin_rec.recommended_product_name, 'Blueberry Muffin')
        self.assertEqual(muffin_rec.recommended_price, Decimal('2.49'))
        
        # Verify event published
        mock_producer.publish.assert_called_once()
        published_data = mock_producer.publish.call_args[0][1]
        self.assertEqual(published_data['event_type'], 'RECOMMENDATION_SUGGESTED')
        self.assertEqual(published_data['basket_id'], 'BASKET-456')
        self.assertEqual(published_data['source_product_id'], 'COFFEE')
        self.assertEqual(len(published_data['recommendations']), 2)
        
        # Verify WebSocket message sent
        mock_async.assert_called_once()