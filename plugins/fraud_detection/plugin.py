from plugins.base import BasePlugin
from .models import FraudRule, FraudAlert
from .state_manager import state_manager
from events.producer import event_producer
from employees.models import Employee
from django.conf import settings
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)


class FraudDetectionPlugin(BasePlugin):
    name = "fraud_detection"
    description = "Detects fraudulent activities in POS transactions"
    
    def get_supported_events(self):
        return [
            "EMPLOYEE_LOGIN", "EMPLOYEE_LOGOUT", "SESSION_TERMINATED",
            "BASKET_STARTED", "item.added", "CUSTOMER_IDENTIFIED", 
            "PAYMENT_COMPLETED"
        ]
    
    def handle_event(self, event_type, event_data):
        """Handle fraud detection events"""
        try:
            employee_id = event_data.get('employee_id')
            terminal_id = event_data.get('terminal_id')
            basket_id = event_data.get('basket_id')
            
            # Update state
            self._update_state(event_type, event_data, employee_id, terminal_id, basket_id)
            
            # Evaluate fraud rules
            self._evaluate_rules(event_type, event_data, employee_id, terminal_id, basket_id)
            
        except Exception as e:
            logger.error(f"Fraud detection error: {e}")
    
    def _update_state(self, event_type, event_data, employee_id, terminal_id, basket_id):
        """Update internal state based on event"""
        if employee_id:
            state_manager.update_employee_session(employee_id, terminal_id, event_type, event_data)
        
        if terminal_id:
            state_manager.update_terminal_state(terminal_id, employee_id, event_type)
        
        if basket_id:
            state_manager.update_basket_state(basket_id, employee_id, terminal_id, event_type, event_data)
    
    def _evaluate_rules(self, event_type, event_data, employee_id, terminal_id, basket_id):
        """Evaluate all enabled fraud rules"""
        rules = FraudRule.objects.filter(enabled=True)
        
        for rule in rules:
            try:
                if self._should_evaluate_rule(rule, event_type):
                    violation = self._check_rule_violation(rule, event_data, employee_id, terminal_id, basket_id)
                    if violation:
                        self._create_alert(rule, violation, employee_id, terminal_id, basket_id)
            except Exception as e:
                logger.error(f"Rule evaluation error for {rule.rule_id}: {e}")
    
    def _should_evaluate_rule(self, rule, event_type):
        """Check if rule should be evaluated for this event type"""
        rule_event_mapping = {
            'multiple_terminals': ['EMPLOYEE_LOGIN'],
            'rapid_items': ['BASKET_STARTED', 'item.added'],  # Need BASKET_STARTED to initialize state
            'high_value_payment': ['PAYMENT_COMPLETED'],
            'anonymous_payment': ['PAYMENT_COMPLETED'],
            'rapid_checkout': ['PAYMENT_COMPLETED']
        }
        return event_type in rule_event_mapping.get(rule.rule_id, [])
    
    def _check_rule_violation(self, rule, event_data, employee_id, terminal_id, basket_id):
        """Check if specific rule is violated"""
        if rule.rule_id == 'multiple_terminals':
            return self._check_multiple_terminals(rule, employee_id)
        elif rule.rule_id == 'rapid_items':
            # For BASKET_STARTED events, just initialize state (no violation yet)
            event_type = event_data.get('event_type')
            if event_type == 'BASKET_STARTED':
                return None  # Just initializing, no violation
            return self._check_rapid_items(rule, basket_id)
        elif rule.rule_id == 'high_value_payment':
            return self._check_high_value_payment(rule, event_data, employee_id)
        elif rule.rule_id == 'anonymous_payment':
            return self._check_anonymous_payment(rule, event_data, basket_id)
        elif rule.rule_id == 'rapid_checkout':
            return self._check_rapid_checkout(rule, basket_id)
        
        return None
    
    def _check_multiple_terminals(self, rule, employee_id):
        """Check if employee is using multiple terminals"""
        session = state_manager.get_employee_session(employee_id)
        if session and len(session['terminal_ids']) >= rule.threshold:
            return {
                'rule_name': rule.name,
                'threshold': rule.threshold,
                'actual_value': len(session['terminal_ids']),
                'terminals': list(session['terminal_ids'])
            }
        return None
    
    def _check_rapid_items(self, rule, basket_id):
        """Check if items are being added too rapidly"""
        basket = state_manager.get_basket_state(basket_id)
        if not basket:
            return None
        
        now = datetime.now()
        recent_items = [
            ts for ts in basket['item_velocity']
            if now - ts <= timedelta(seconds=rule.time_window)
        ]
        
        if len(recent_items) >= rule.threshold:
            return {
                'rule_name': rule.name,
                'threshold': rule.threshold,
                'actual_value': len(recent_items),
                'time_window': rule.time_window
            }
        return None
    
    def _check_high_value_payment(self, rule, event_data, employee_id):
        """Check if payment amount is unusually high for short session"""
        session = state_manager.get_employee_session(employee_id)
        if not session:
            return None
        
        session_duration = (datetime.now() - session['login_time']).total_seconds()
        payment_amount = event_data.get('amount', 0)
        
        if session_duration <= rule.time_window and payment_amount >= rule.threshold:
            return {
                'rule_name': rule.name,
                'threshold': rule.threshold,
                'actual_value': payment_amount,
                'session_duration': session_duration
            }
        return None
    
    def _check_anonymous_payment(self, rule, event_data, basket_id):
        """Check if high-value payment completed without customer identification"""
        basket = state_manager.get_basket_state(basket_id)
        if not basket:
            return None
        
        payment_amount = event_data.get('amount', 0)
        
        if payment_amount >= rule.threshold and not basket['customer_identified']:
            return {
                'rule_name': rule.name,
                'threshold': rule.threshold,
                'actual_value': payment_amount,
                'customer_identified': False
            }
        return None
    
    def _check_rapid_checkout(self, rule, basket_id):
        """Check if basket was started and completed too quickly"""
        basket = state_manager.get_basket_state(basket_id)
        if not basket:
            return None
        
        checkout_duration = (datetime.now() - basket['start_time']).total_seconds()
        
        if checkout_duration <= rule.time_window:
            return {
                'rule_name': rule.name,
                'threshold': rule.time_window,
                'actual_value': checkout_duration,
                'item_count': basket['item_count']
            }
        return None
    
    def _create_alert(self, rule, violation_details, employee_id, terminal_id, basket_id):
        """Create and publish fraud alert"""
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # Get terminal_id from basket state if not provided
            if not terminal_id and basket_id:
                basket_state = state_manager.get_basket_state(basket_id)
                if basket_state:
                    terminal_id = basket_state.get('terminal_id')
            
            # Create alert record
            alert = FraudAlert.objects.create(
                rule=rule,
                employee=employee,
                terminal_id=terminal_id,
                basket_id=basket_id,
                severity=rule.severity,
                details=violation_details
            )
            
            # Send real-time alert to WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            
            # For multiple terminals fraud, send alert to all affected terminals
            if rule.rule_id == 'multiple_terminals' and 'terminals' in violation_details:
                for affected_terminal_id in violation_details['terminals']:
                    async_to_sync(channel_layer.group_send)(
                        f'fraud_alerts_{affected_terminal_id}',
                        {
                            'type': 'fraud_alert',
                            'alert_id': str(alert.alert_id),
                            'rule_id': rule.rule_id,
                            'severity': rule.severity,
                            'details': violation_details,
                            'timestamp': alert.timestamp.isoformat()
                        }
                    )
            else:
                # Send to current terminal
                if terminal_id:
                    async_to_sync(channel_layer.group_send)(
                        f'fraud_alerts_{terminal_id}',
                        {
                            'type': 'fraud_alert',
                            'alert_id': str(alert.alert_id),
                            'rule_id': rule.rule_id,
                            'severity': rule.severity,
                            'details': violation_details,
                            'timestamp': alert.timestamp.isoformat()
                        }
                    )
            
            # Publish fraud alert event
            alert_event = {
                'event_type': 'fraud.alert',
                'timestamp': datetime.now().isoformat(),
                'alert_id': str(alert.alert_id),
                'rule_id': rule.rule_id,
                'severity': rule.severity,
                'employee_id': employee_id,
                'terminal_id': terminal_id,
                'basket_id': basket_id,
                'details': violation_details,
                'metadata': {
                    'plugin_version': '1.0.0',
                    'detection_time': datetime.now().isoformat()
                }
            }
            
            event_producer.publish(settings.KAFKA_TOPIC, alert_event)
            logger.warning(f"FRAUD ALERT: {rule.name} - Employee {employee.username} - {violation_details}")
            
        except Exception as e:
            logger.error(f"Failed to create fraud alert: {e}")