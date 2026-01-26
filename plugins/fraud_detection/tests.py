from django.test import TestCase
from unittest.mock import patch, Mock
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta

from plugins.models import PluginConfiguration
from plugins.fraud_detection.plugin import FraudDetectionPlugin
from plugins.fraud_detection.models import FraudRule, FraudAlert
from plugins.fraud_detection.state_manager import state_manager
from employees.models import Employee


class FraudDetectionPluginTest(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.plugin_config = PluginConfiguration.objects.create(
            name='fraud_detection',
            enabled=True,
            config={}
        )
        
        self.plugin = FraudDetectionPlugin()
        
        # Create test employee
        self.employee = Employee.objects.create_user(
            username='testuser',
            password='testpass123',
            employee_id='EMP001',
            first_name='Test',
            last_name='User',
            role='CASHIER'
        )
        
        # Create fraud rules
        self.multiple_terminals_rule = FraudRule.objects.create(
            rule_id='multiple_terminals',
            name='Multiple Terminal Access',
            description='Employee accessing multiple terminals simultaneously',
            severity='HIGH',
            time_window=300,
            threshold=2,
            enabled=True
        )
        
        self.rapid_items_rule = FraudRule.objects.create(
            rule_id='rapid_items',
            name='Rapid Item Addition',
            description='Items being added too quickly',
            severity='MEDIUM',
            time_window=30,
            threshold=5,
            enabled=True
        )
        
        self.high_value_rule = FraudRule.objects.create(
            rule_id='high_value_payment',
            name='High Value Payment',
            description='High value payment in short session',
            severity='CRITICAL',
            time_window=60,
            threshold=1000,
            enabled=True
        )
        
        # Clear state manager for clean tests
        state_manager.employee_sessions.clear()
        state_manager.terminal_states.clear()
        state_manager.basket_states.clear()
    
    def test_plugin_processes_events_when_enabled(self):
        """Test plugin processes fraud detection events when enabled"""
        supported_events = self.plugin.get_supported_events()
        expected_events = [
            "EMPLOYEE_LOGIN", "EMPLOYEE_LOGOUT", "SESSION_TERMINATED",
            "BASKET_STARTED", "item.added", "CUSTOMER_IDENTIFIED", 
            "PAYMENT_COMPLETED"
        ]
        
        for event in expected_events:
            self.assertIn(event, supported_events)
        
        # Test event handling
        event_data = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001'
        }
        
        with patch.object(self.plugin, '_evaluate_rules') as mock_evaluate:
            self.plugin.handle_event('EMPLOYEE_LOGIN', event_data)
            mock_evaluate.assert_called_once()
    
    def test_plugin_ignores_events_when_disabled(self):
        """Test plugin ignores events when disabled via registry"""
        # Disable plugin
        self.plugin_config.enabled = False
        self.plugin_config.save()
        
        # Test that disabled plugin is not returned by registry
        from plugins.registry import plugin_registry
        enabled_plugins = plugin_registry.get_enabled_plugins()
        plugin_names = [p.name for p in enabled_plugins]
        self.assertNotIn('fraud_detection', plugin_names)
    
    @patch('asgiref.sync.async_to_sync')
    @patch('plugins.fraud_detection.plugin.event_producer')
    def test_multiple_terminals_fraud_detection(self, mock_producer, mock_async):
        """Test detection of multiple terminal access fraud"""
        # Simulate employee logging into first terminal
        event_data_1 = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001'
        }
        self.plugin.handle_event('EMPLOYEE_LOGIN', event_data_1)
        
        # Simulate employee logging into second terminal (should trigger alert)
        event_data_2 = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-002'
        }
        self.plugin.handle_event('EMPLOYEE_LOGIN', event_data_2)
        
        # Should create fraud alert
        alert = FraudAlert.objects.get(rule=self.multiple_terminals_rule)
        self.assertEqual(alert.employee, self.employee)
        self.assertEqual(alert.severity, 'HIGH')
        self.assertIn('terminals', alert.details)
        self.assertEqual(len(alert.details['terminals']), 2)
        
        # Should publish event
        mock_producer.publish.assert_called_once()
        
        # Should send WebSocket message
        mock_async.assert_called()
    
    @patch('asgiref.sync.async_to_sync')
    @patch('plugins.fraud_detection.plugin.event_producer')
    def test_rapid_items_fraud_detection(self, mock_producer, mock_async):
        """Test detection of rapid item addition fraud"""
        # Start basket
        basket_event = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'basket_id': 'BASKET-123'
        }
        self.plugin.handle_event('BASKET_STARTED', basket_event)
        
        # Add items rapidly (should trigger alert on 5th item)
        for i in range(5):
            item_event = {
                'employee_id': self.employee.id,
                'terminal_id': 'TERM-001',
                'basket_id': 'BASKET-123',
                'product_id': f'ITEM-{i}'
            }
            self.plugin.handle_event('item.added', item_event)
        
        # Should create fraud alert
        alert = FraudAlert.objects.get(rule=self.rapid_items_rule)
        self.assertEqual(alert.employee, self.employee)
        self.assertEqual(alert.severity, 'MEDIUM')
        self.assertEqual(alert.details['actual_value'], 5)
        
        # Should publish event
        mock_producer.publish.assert_called()
    
    @patch('asgiref.sync.async_to_sync')
    @patch('plugins.fraud_detection.plugin.event_producer')
    def test_high_value_payment_fraud_detection(self, mock_producer, mock_async):
        """Test detection of high value payment fraud"""
        # Employee login
        login_event = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001'
        }
        self.plugin.handle_event('EMPLOYEE_LOGIN', login_event)
        
        # High value payment within short session (should trigger alert)
        payment_event = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'basket_id': 'BASKET-123',
            'amount': 1500.00
        }
        self.plugin.handle_event('PAYMENT_COMPLETED', payment_event)
        
        # Should create fraud alert
        alert = FraudAlert.objects.get(rule=self.high_value_rule)
        self.assertEqual(alert.employee, self.employee)
        self.assertEqual(alert.severity, 'CRITICAL')
        self.assertEqual(alert.details['actual_value'], 1500.00)
        
        # Should publish event
        mock_producer.publish.assert_called()
    
    def test_no_alert_when_rule_disabled(self):
        """Test no alert created when rule is disabled"""
        # Disable rule
        self.multiple_terminals_rule.enabled = False
        self.multiple_terminals_rule.save()
        
        # Simulate multiple terminal access
        event_data_1 = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001'
        }
        self.plugin.handle_event('EMPLOYEE_LOGIN', event_data_1)
        
        event_data_2 = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-002'
        }
        self.plugin.handle_event('EMPLOYEE_LOGIN', event_data_2)
        
        # Should not create alert
        alerts = FraudAlert.objects.filter(rule=self.multiple_terminals_rule)
        self.assertEqual(alerts.count(), 0)
    
    def test_state_manager_updates(self):
        """Test state manager properly tracks state"""
        # Test employee session tracking
        event_data = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001'
        }
        self.plugin.handle_event('EMPLOYEE_LOGIN', event_data)
        
        session = state_manager.get_employee_session(self.employee.id)
        self.assertIsNotNone(session)
        self.assertIn('TERM-001', session['terminal_ids'])
        
        # Test basket state tracking
        basket_event = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'basket_id': 'BASKET-123'
        }
        self.plugin.handle_event('BASKET_STARTED', basket_event)
        
        basket_state = state_manager.get_basket_state('BASKET-123')
        self.assertIsNotNone(basket_state)
        self.assertEqual(basket_state['employee_id'], self.employee.id)
        self.assertEqual(basket_state['terminal_id'], 'TERM-001')
    
    @patch('asgiref.sync.async_to_sync')
    @patch('plugins.fraud_detection.plugin.event_producer')
    def test_complete_fraud_detection_workflow(self, mock_producer, mock_async):
        """Test complete fraud detection workflow"""
        # Create anonymous payment rule
        anonymous_rule = FraudRule.objects.create(
            rule_id='anonymous_payment',
            name='Anonymous High Value Payment',
            description='High value payment without customer identification',
            severity='HIGH',
            time_window=300,
            threshold=500,
            enabled=True
        )
        
        # Start basket
        basket_event = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'basket_id': 'BASKET-456'
        }
        self.plugin.handle_event('BASKET_STARTED', basket_event)
        
        # Complete high value payment without customer identification
        payment_event = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'basket_id': 'BASKET-456',
            'amount': 750.00
        }
        self.plugin.handle_event('PAYMENT_COMPLETED', payment_event)
        
        # Verify alert created
        alert = FraudAlert.objects.get(rule=anonymous_rule)
        self.assertEqual(alert.employee, self.employee)
        self.assertEqual(alert.terminal_id, 'TERM-001')
        self.assertEqual(alert.basket_id, 'BASKET-456')
        self.assertEqual(alert.severity, 'HIGH')
        self.assertEqual(alert.details['actual_value'], 750.00)
        self.assertFalse(alert.details['customer_identified'])
        self.assertFalse(alert.acknowledged)
        
        # Verify event published
        mock_producer.publish.assert_called_once()
        published_data = mock_producer.publish.call_args[0][1]
        self.assertEqual(published_data['event_type'], 'fraud.alert')
        self.assertEqual(published_data['rule_id'], 'anonymous_payment')
        self.assertEqual(published_data['severity'], 'HIGH')
        self.assertEqual(published_data['employee_id'], self.employee.id)
        
        # Verify WebSocket message sent
        mock_async.assert_called_once()