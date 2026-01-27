from django.test import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal
from django.utils import timezone

from plugins.models import PluginConfiguration
from plugins.age_verification.plugin import AgeVerificationPlugin
from plugins.age_verification.models import AgeVerificationState, AgeVerificationViolation
from plugins.age_verification.state_manager import state_manager
from products.models import Product
from baskets.models import Basket, BasketItem
from employees.models import Employee


class AgeVerificationPluginTest(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.plugin_config = PluginConfiguration.objects.create(
            name='age_verification',
            enabled=True,
            config={}
        )
        
        self.plugin = AgeVerificationPlugin()
        
        # Create test employee
        self.employee = Employee.objects.create_user(
            username='testuser',
            password='testpass123',
            employee_id='EMP001',
            first_name='Test',
            last_name='User',
            role='CASHIER'
        )
        
        # Create test products
        self.beer = Product.objects.create(
            product_id='BEER001',
            name='Beer',
            price=Decimal('4.99'),
            category='Alcohol',
            age_restricted=True,
            minimum_age=21,
            age_restriction_category='ALCOHOL'
        )
        
        self.cigarettes = Product.objects.create(
            product_id='CIG001',
            name='Cigarettes',
            price=Decimal('8.99'),
            category='Tobacco',
            age_restricted=True,
            minimum_age=18,
            age_restriction_category='TOBACCO'
        )
        
        self.soda = Product.objects.create(
            product_id='SODA001',
            name='Soda',
            price=Decimal('1.99'),
            category='Beverage',
            age_restricted=False
        )
        
        # Create test basket
        self.basket = Basket.objects.create(
            basket_id='BASKET-123',
            employee=self.employee,
            status='ACTIVE'
        )
        
        # Clear any existing state
        AgeVerificationState.objects.all().delete()
    
    def test_plugin_processes_events_when_enabled(self):
        """Test plugin processes age verification events when enabled"""
        supported_events = self.plugin.get_supported_events()
        expected_events = [
            "basket.started", "item.added", "item.removed",
            "age.verified", "age.verification.cancelled", "age.verification.completed",
            "payment.initiated", "payment.completed"
        ]
        
        for event in expected_events:
            self.assertIn(event, supported_events)
        
        # Test event handling
        event_data = {'basket_id': 'BASKET-123'}
        
        with patch.object(self.plugin, '_handle_basket_started') as mock_handle:
            self.plugin.handle_event('basket.started', event_data)
            mock_handle.assert_called_once_with('BASKET-123')
    
    def test_plugin_ignores_events_when_disabled(self):
        """Test plugin ignores events when disabled via registry"""
        # Disable plugin
        self.plugin_config.enabled = False
        self.plugin_config.save()
        
        # Test that disabled plugin is not returned by registry
        from plugins.registry import plugin_registry
        enabled_plugins = plugin_registry.get_enabled_plugins()
        plugin_names = [p.name for p in enabled_plugins]
        self.assertNotIn('age_verification', plugin_names)
    
    def test_basket_started_creates_state(self):
        """Test basket started event creates verification state"""
        event_data = {'basket_id': 'BASKET-123'}
        
        self.plugin.handle_event('basket.started', event_data)
        
        # Should create state
        state = AgeVerificationState.objects.get(basket_id='BASKET-123')
        self.assertFalse(state.requires_verification)
        self.assertFalse(state.verification_completed)
    
    @patch('plugins.age_verification.plugin.event_producer')
    def test_age_restricted_item_triggers_verification(self, mock_producer):
        """Test adding age-restricted item triggers verification requirement"""
        # Start basket first
        self.plugin.handle_event('basket.started', {'basket_id': 'BASKET-123'})
        
        # Add age-restricted item
        event_data = {
            'basket_id': 'BASKET-123',
            'product_id': 'BEER001',
            'age_restricted': True,
            'quantity': 1,
            'price': 4.99
        }
        
        self.plugin.handle_event('item.added', event_data)
        
        # Should update state to require verification
        state = AgeVerificationState.objects.get(basket_id='BASKET-123')
        self.assertTrue(state.requires_verification)
        self.assertEqual(len(state.restricted_items), 1)
        self.assertEqual(state.restricted_items[0]['productId'], 'BEER001')
        self.assertEqual(state.restricted_items[0]['minimum_age'], 21)
        
        # Should publish verification required event
        mock_producer.publish.assert_called_once()
        published_data = mock_producer.publish.call_args[0][1]
        self.assertEqual(published_data['event_type'], 'age.verification.required')
        self.assertEqual(published_data['basket_id'], 'BASKET-123')
    
    def test_non_restricted_item_no_verification(self):
        """Test adding non-restricted item doesn't trigger verification"""
        # Start basket first
        self.plugin.handle_event('basket.started', {'basket_id': 'BASKET-123'})
        
        # Add non-restricted item
        event_data = {
            'basket_id': 'BASKET-123',
            'product_id': 'SODA001',
            'age_restricted': False,
            'quantity': 1,
            'price': 1.99
        }
        
        with patch('plugins.age_verification.plugin.event_producer') as mock_producer:
            self.plugin.handle_event('item.added', event_data)
        
        # Should not require verification
        state = AgeVerificationState.objects.get(basket_id='BASKET-123')
        self.assertFalse(state.requires_verification)
        self.assertEqual(len(state.restricted_items), 0)
        
        # Should not publish verification event
        mock_producer.publish.assert_not_called()
    
    @patch('plugins.age_verification.plugin.event_producer')
    def test_age_verification_success(self, mock_producer):
        """Test successful age verification"""
        # Setup basket with restricted item
        self.plugin.handle_event('basket.started', {'basket_id': 'BASKET-123'})
        self.plugin.handle_event('item.added', {
            'basket_id': 'BASKET-123',
            'product_id': 'BEER001',
            'age_restricted': True,
            'quantity': 1,
            'price': 4.99
        })
        
        # Verify age (customer is 25, beer requires 21)
        event_data = {
            'basket_id': 'BASKET-123',
            'verifier_employee_id': self.employee.id,
            'customer_age': 25,
            'verification_method': 'ID_CHECK'
        }
        
        self.plugin.handle_event('age.verified', event_data)
        
        # Should complete verification
        state = AgeVerificationState.objects.get(basket_id='BASKET-123')
        self.assertTrue(state.verification_completed)
        self.assertEqual(state.customer_age, 25)
        self.assertEqual(state.verification_method, 'ID_CHECK')
        
        # Should publish verification completed event
        mock_producer.publish.assert_called()
        published_data = mock_producer.publish.call_args[0][1]
        self.assertEqual(published_data['event_type'], 'age.verification.completed')
    
    @patch('plugins.age_verification.plugin.event_producer')
    def test_age_verification_failure(self, mock_producer):
        """Test failed age verification (insufficient age)"""
        # Setup basket with restricted item
        self.plugin.handle_event('basket.started', {'basket_id': 'BASKET-123'})
        self.plugin.handle_event('item.added', {
            'basket_id': 'BASKET-123',
            'product_id': 'BEER001',
            'age_restricted': True,
            'quantity': 1,
            'price': 4.99
        })
        
        # Verify age (customer is 18, beer requires 21)
        event_data = {
            'basket_id': 'BASKET-123',
            'verifier_employee_id': self.employee.id,
            'customer_age': 18,
            'verification_method': 'ID_CHECK'
        }
        
        self.plugin.handle_event('age.verified', event_data)
        
        # Should publish verification failed event
        mock_producer.publish.assert_called()
        published_data = mock_producer.publish.call_args[0][1]
        self.assertEqual(published_data['event_type'], 'age.verification.failed')
        self.assertEqual(published_data['reason'], 'INSUFFICIENT_AGE')
    
    @patch('plugins.age_verification.plugin.event_producer')
    def test_payment_blocked_without_verification(self, mock_producer):
        """Test payment is blocked when verification is required but not completed"""
        # Setup basket with restricted item
        self.plugin.handle_event('basket.started', {'basket_id': 'BASKET-123'})
        self.plugin.handle_event('item.added', {
            'basket_id': 'BASKET-123',
            'product_id': 'BEER001',
            'age_restricted': True,
            'quantity': 1,
            'price': 4.99
        })
        
        # Attempt payment without verification
        event_data = {
            'basket_id': 'BASKET-123',
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'amount': 4.99
        }
        
        self.plugin.handle_event('payment.initiated', event_data)
        
        # Should create violation
        violation = AgeVerificationViolation.objects.get(basket_id='BASKET-123')
        self.assertEqual(violation.employee, self.employee)
        self.assertEqual(violation.violation_type, 'UNVERIFIED_RESTRICTED_ITEMS')
        
        # Should publish verification failed event
        mock_producer.publish.assert_called()
        published_data = mock_producer.publish.call_args[0][1]
        self.assertEqual(published_data['event_type'], 'age.verification.failed')
        self.assertEqual(published_data['reason'], 'UNVERIFIED_RESTRICTED_ITEMS')
    
    @patch('plugins.age_verification.plugin.event_producer')
    def test_verification_completed_adds_items_to_basket(self, mock_producer):
        """Test verification completion adds verified items to basket"""
        # Setup basket with restricted item
        self.plugin.handle_event('basket.started', {'basket_id': 'BASKET-123'})
        self.plugin.handle_event('item.added', {
            'basket_id': 'BASKET-123',
            'product_id': 'BEER001',
            'age_restricted': True,
            'quantity': 2,
            'price': 4.99
        })
        
        # Complete age verification (this now adds items to basket)
        self.plugin.handle_event('age.verified', {
            'basket_id': 'BASKET-123',
            'verifier_employee_id': self.employee.id,
            'customer_age': 25,
            'verification_method': 'ID_CHECK'
        })
        
        # Should add item to basket
        basket_item = BasketItem.objects.get(basket=self.basket, product_id='BEER001')
        self.assertEqual(basket_item.product_name, 'Beer')
        self.assertEqual(basket_item.quantity, 2)
        self.assertEqual(basket_item.price, Decimal('4.99'))
        
        # Should publish verified item added event (check the first call which is verified.item.added)
        mock_producer.publish.assert_called()
        # Get all calls to find the verified.item.added event
        calls = mock_producer.publish.call_args_list
        verified_item_call = None
        for call in calls:
            if call[0][1]['event_type'] == 'verified.item.added':
                verified_item_call = call
                break
        
        self.assertIsNotNone(verified_item_call, "verified.item.added event should be published")
        published_data = verified_item_call[0][1]
        self.assertEqual(published_data['event_type'], 'verified.item.added')
        self.assertEqual(published_data['product_id'], 'BEER001')
    
    def test_payment_completed_clears_state(self):
        """Test payment completion clears verification state"""
        # Setup basket with state
        self.plugin.handle_event('basket.started', {'basket_id': 'BASKET-123'})
        
        # Verify state exists
        self.assertTrue(AgeVerificationState.objects.filter(basket_id='BASKET-123').exists())
        
        # Complete payment
        self.plugin.handle_event('payment.completed', {'basket_id': 'BASKET-123'})
        
        # Should clear state
        self.assertFalse(AgeVerificationState.objects.filter(basket_id='BASKET-123').exists())
    
    @patch('plugins.age_verification.plugin.event_producer')
    def test_complete_age_verification_workflow(self, mock_producer):
        """Test complete age verification workflow"""
        # Start basket
        self.plugin.handle_event('basket.started', {'basket_id': 'BASKET-456'})
        
        # Add multiple restricted items
        self.plugin.handle_event('item.added', {
            'basket_id': 'BASKET-456',
            'product_id': 'BEER001',
            'age_restricted': True,
            'quantity': 1,
            'price': 4.99
        })
        
        self.plugin.handle_event('item.added', {
            'basket_id': 'BASKET-456',
            'product_id': 'CIG001',
            'age_restricted': True,
            'quantity': 1,
            'price': 8.99
        })
        
        # Verify state requires verification
        state = AgeVerificationState.objects.get(basket_id='BASKET-456')
        self.assertTrue(state.requires_verification)
        self.assertEqual(len(state.restricted_items), 2)
        
        # Complete age verification (customer is 25, meets both requirements)
        self.plugin.handle_event('age.verified', {
            'basket_id': 'BASKET-456',
            'verifier_employee_id': self.employee.id,
            'customer_age': 25,
            'verification_method': 'ID_CHECK'
        })
        
        # Verify completion
        state.refresh_from_db()
        self.assertTrue(state.verification_completed)
        self.assertEqual(state.customer_age, 25)
        
        # Verify events published
        self.assertEqual(mock_producer.publish.call_count, 3)  # 2 required + 1 completed
        
        # Clean up
        self.plugin.handle_event('payment.completed', {'basket_id': 'BASKET-456'})
        self.assertFalse(AgeVerificationState.objects.filter(basket_id='BASKET-456').exists())