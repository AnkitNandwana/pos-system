from plugins.base import BasePlugin
from .models import AgeVerificationViolation
from .state_manager import state_manager
from events.producer import event_producer
from employees.models import Employee
from products.models import Product
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgeVerificationPlugin(BasePlugin):
    name = "age_verification"
    description = "Enforces age verification for restricted products"
    
    def get_supported_events(self):
        return [
            "basket.started", "item.added", "item.removed", 
            "age.verified", "payment.initiated", "payment.completed"
        ]
    
    def handle_event(self, event_type, event_data):
        """Handle age verification events"""
        try:
            basket_id = event_data.get('basket_id')
            employee_id = event_data.get('employee_id')
            terminal_id = event_data.get('terminal_id')
            
            logger.info(f"[AGE VERIFICATION] Processing event: {event_type} for basket {basket_id}")
            
            if event_type == "basket.started":
                self._handle_basket_started(basket_id)
            elif event_type == "item.added":
                self._handle_item_added(event_data, basket_id)
            elif event_type == "item.removed":
                self._handle_item_removed(event_data, basket_id)
            elif event_type == "age.verified":
                self._handle_age_verified(event_data, basket_id)
            elif event_type == "payment.initiated":
                self._handle_payment_initiated(event_data, basket_id, employee_id, terminal_id)
            elif event_type == "payment.completed":
                self._handle_payment_completed(basket_id)
                
        except Exception as e:
            logger.error(f"Age verification error: {e}")
    
    def _handle_basket_started(self, basket_id):
        """Initialize basket verification state"""
        if basket_id:
            state_manager.create_basket_state(basket_id)
            logger.info(f"[AGE VERIFICATION] Initialized state for basket {basket_id}")
    
    def _handle_item_added(self, event_data, basket_id):
        """Check if added item requires age verification"""
        if not basket_id:
            return
            
        product_id = event_data.get('product_id')
        if not product_id:
            return
        
        try:
            product = Product.objects.get(product_id=product_id)
            
            if product.age_restricted:
                # Get current state
                current_state = state_manager.get_basket_state(basket_id)
                restricted_items = current_state['restricted_items'] if current_state else []
                
                # Add new restricted item
                restricted_item = {
                    'product_id': product.product_id,
                    'name': product.name,
                    'minimum_age': product.minimum_age,
                    'category': product.age_restriction_category or product.category
                }
                
                # Avoid duplicates
                if not any(item['product_id'] == product_id for item in restricted_items):
                    restricted_items.append(restricted_item)
                
                # Update state
                state_manager.update_verification_requirement(basket_id, restricted_items)
                
                # Publish verification required event
                self._publish_verification_required(basket_id, restricted_items)
                
                logger.info(f"[AGE VERIFICATION] Age-restricted item added: {product.name}")
                
        except Product.DoesNotExist:
            logger.warning(f"Product {product_id} not found")
    
    def _handle_item_removed(self, event_data, basket_id):
        """Recalculate verification requirements after item removal"""
        if not basket_id:
            return
            
        product_id = event_data.get('product_id')
        current_state = state_manager.get_basket_state(basket_id)
        
        if current_state and current_state['restricted_items']:
            # Remove item from restricted items
            restricted_items = [
                item for item in current_state['restricted_items'] 
                if item['product_id'] != product_id
            ]
            
            # Update state
            state_manager.update_verification_requirement(basket_id, restricted_items)
            
            logger.info(f"[AGE VERIFICATION] Recalculated requirements after item removal")
    
    def _handle_age_verified(self, event_data, basket_id):
        """Handle age verification completion"""
        if not basket_id:
            return
            
        verifier_id = event_data.get('verifier_employee_id')
        customer_age = event_data.get('customer_age')
        verification_method = event_data.get('verification_method', 'MANUAL_CHECK')
        
        state_manager.complete_verification(basket_id, verifier_id, customer_age, verification_method)
        
        # Publish verification completed event
        self._publish_verification_completed(basket_id, customer_age, verification_method, verifier_id)
        
        logger.info(f"[AGE VERIFICATION] Verification completed for basket {basket_id}")
    
    def _handle_payment_initiated(self, event_data, basket_id, employee_id, terminal_id):
        """Enforce age verification before payment"""
        if not basket_id:
            return
            
        if state_manager.is_verification_required(basket_id):
            if not state_manager.is_verification_completed(basket_id):
                # Block payment - verification required but not completed
                self._create_violation(
                    basket_id, employee_id, terminal_id,
                    'UNVERIFIED_RESTRICTED_ITEMS',
                    {'reason': 'Payment attempted with unverified age-restricted items'}
                )
                
                # Publish verification failed event
                self._publish_verification_failed(basket_id, employee_id, 'UNVERIFIED_RESTRICTED_ITEMS')
                
                logger.warning(f"[AGE VERIFICATION] Payment blocked for basket {basket_id} - verification required")
    
    def _handle_payment_completed(self, basket_id):
        """Clean up verification state after payment"""
        if basket_id:
            state_manager.clear_basket_state(basket_id)
            logger.info(f"[AGE VERIFICATION] Cleaned up state for basket {basket_id}")
    
    def _publish_verification_required(self, basket_id, restricted_items):
        """Publish age verification required event"""
        event = {
            'event_type': 'age.verification.required',
            'timestamp': datetime.now().isoformat(),
            'basket_id': basket_id,
            'restricted_items': restricted_items,
            'minimum_age': max(item['minimum_age'] for item in restricted_items) if restricted_items else 18
        }
        event_producer.publish(settings.KAFKA_TOPIC, event)
    
    def _publish_verification_completed(self, basket_id, customer_age, verification_method, verifier_id):
        """Publish age verification completed event"""
        event = {
            'event_type': 'age.verification.completed',
            'timestamp': datetime.now().isoformat(),
            'basket_id': basket_id,
            'customer_age': customer_age,
            'verification_method': verification_method,
            'verifier_id': verifier_id
        }
        event_producer.publish(settings.KAFKA_TOPIC, event)
    
    def _publish_verification_failed(self, basket_id, employee_id, reason):
        """Publish age verification failed event"""
        event = {
            'event_type': 'age.verification.failed',
            'timestamp': datetime.now().isoformat(),
            'basket_id': basket_id,
            'employee_id': employee_id,
            'reason': reason,
            'action_required': 'VERIFY_AGE_OR_REMOVE_ITEMS'
        }
        event_producer.publish(settings.KAFKA_TOPIC, event)
    
    def _create_violation(self, basket_id, employee_id, terminal_id, violation_type, details):
        """Create age verification violation record"""
        try:
            employee = Employee.objects.get(id=employee_id)
            
            violation = AgeVerificationViolation.objects.create(
                basket_id=basket_id,
                employee=employee,
                terminal_id=terminal_id,
                violation_type=violation_type,
                details=details
            )
            
            logger.warning(f"🚨 AGE VERIFICATION VIOLATION: {violation_type} - Basket {basket_id} - Employee {employee.username}")
            
        except Exception as e:
            logger.error(f"Failed to create age verification violation: {e}")