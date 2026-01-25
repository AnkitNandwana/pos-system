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
            "age.verified", "age.verification.cancelled", "age.verification.completed", 
            "payment.initiated", "payment.completed"
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
            elif event_type == "age.verification.cancelled":
                self._handle_age_verification_cancelled(event_data, basket_id)
            elif event_type == "age.verification.completed":
                self._handle_age_verification_completed(event_data, basket_id)
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
        logger.info(f"[AGE VERIFICATION] Processing item.added event for basket {basket_id}")
        logger.info(f"[AGE VERIFICATION] Event data: {event_data}")
        
        if not basket_id:
            logger.warning(f"[AGE VERIFICATION] No basket_id provided")
            return
            
        product_id = event_data.get('product_id')
        age_restricted = event_data.get('age_restricted', False)
        
        logger.info(f"[AGE VERIFICATION] Product {product_id}, age_restricted: {age_restricted}")
        
        if not product_id or not age_restricted:
            logger.info(f"[AGE VERIFICATION] Skipping - not age restricted")
            return
        
        try:
            product = Product.objects.get(product_id=product_id)
            logger.info(f"[AGE VERIFICATION] Found product: {product.name}, age_restricted: {product.age_restricted}")
            
            if product.age_restricted:
                # Get current state
                current_state = state_manager.get_basket_state(basket_id)
                restricted_items = current_state['restricted_items'] if current_state else []
                
                # Add new restricted item
                restricted_item = {
                    'productId': product.product_id,
                    'name': product.name,
                    'minimum_age': product.minimum_age,
                    'category': product.age_restriction_category or product.category,
                    'quantity': event_data.get('quantity', 1),
                    'price': event_data.get('price', float(product.price))
                }
                
                # Avoid duplicates
                if not any(item['productId'] == product_id for item in restricted_items):
                    restricted_items.append(restricted_item)
                
                # Update state
                state_manager.update_verification_requirement(basket_id, restricted_items)
                
                # Publish verification required event - this will trigger frontend subscription
                self._publish_verification_required(basket_id, restricted_items)
                
                logger.info(f"[AGE VERIFICATION] Published verification required event for {product.name}")
                
        except Product.DoesNotExist:
            logger.warning(f"[AGE VERIFICATION] Product {product_id} not found")
    
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
        """Handle age verification completion and allow item addition"""
        if not basket_id:
            return
            
        verifier_id = event_data.get('verifier_employee_id')
        customer_age = event_data.get('customer_age')
        verification_method = event_data.get('verification_method', 'MANUAL_CHECK')
        
        # Complete verification in state
        state_manager.complete_verification(basket_id, verifier_id, customer_age, verification_method)
        
        # Get pending restricted items
        current_state = state_manager.get_basket_state(basket_id)
        if current_state and current_state['restricted_items']:
            # Check if customer meets age requirement
            max_required_age = max(item['minimum_age'] for item in current_state['restricted_items'])
            
            if customer_age >= max_required_age:
                # Age verification passed - publish completion event
                self._publish_verification_completed(basket_id, customer_age, verification_method, verifier_id)
                logger.info(f"[AGE VERIFICATION] Verification completed for basket {basket_id} - customer age {customer_age}")
            else:
                # Age verification failed
                self._publish_verification_failed(basket_id, verifier_id, 'INSUFFICIENT_AGE')
                logger.warning(f"[AGE VERIFICATION] Verification failed - customer age {customer_age} insufficient")
    
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
        """Publish age verification required event for GraphQL subscription"""
        event = {
            'event_type': 'age.verification.required',
            'timestamp': datetime.now().isoformat(),
            'basket_id': basket_id,
            'restricted_items': restricted_items,
            'minimum_age': max(item['minimum_age'] for item in restricted_items) if restricted_items else 18,
            'message': f"Age verification required for {len(restricted_items)} item(s)"
        }
        event_producer.publish(settings.KAFKA_TOPIC, event)
    
    def _publish_verification_completed(self, basket_id, customer_age, verification_method, verifier_id):
        """Publish age verification completed event for GraphQL subscription"""
        event = {
            'event_type': 'age.verification.completed',
            'timestamp': datetime.now().isoformat(),
            'basket_id': basket_id,
            'customer_age': customer_age,
            'verification_method': verification_method,
            'verifier_id': verifier_id,
            'message': 'Age verification completed successfully'
        }
        event_producer.publish(settings.KAFKA_TOPIC, event)
    
    def _publish_verification_failed(self, basket_id, employee_id, reason):
        """Publish age verification failed event for GraphQL subscription"""
        event = {
            'event_type': 'age.verification.failed',
            'timestamp': datetime.now().isoformat(),
            'basket_id': basket_id,
            'employee_id': employee_id,
            'reason': reason,
            'action_required': 'VERIFY_AGE_OR_REMOVE_ITEMS',
            'message': f'Age verification failed: {reason}'
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
    
    def _handle_age_verification_cancelled(self, event_data, basket_id):
        """Handle age verification cancellation"""
        if not basket_id:
            return
            
        employee_id = event_data.get('employee_id')
        
        # Clear verification state
        state_manager.clear_basket_state(basket_id)
        
        # Publish verification failed event
        self._publish_verification_failed(basket_id, employee_id, 'VERIFICATION_CANCELLED')
        
        logger.info(f"[AGE VERIFICATION] Verification cancelled for basket {basket_id}")
    
    def _handle_age_verification_completed(self, event_data, basket_id):
        """Add verified items to basket after age verification completion"""
        if not basket_id:
            return
            
        logger.info(f"[AGE VERIFICATION] Processing verification completion for basket {basket_id}")
        
        # Get restricted items from state
        current_state = state_manager.get_basket_state(basket_id)
        if not current_state or not current_state['restricted_items']:
            logger.warning(f"[AGE VERIFICATION] No restricted items found for basket {basket_id}")
            return
        
        restricted_items = current_state['restricted_items']
        logger.info(f"[AGE VERIFICATION] Found {len(restricted_items)} items to add: {restricted_items}")
        
        # Add each verified item to the basket
        from baskets.models import Basket, BasketItem
        try:
            basket = Basket.objects.get(basket_id=basket_id)
            
            for item in restricted_items:
                product_id = item.get('productId')
                product_name = item.get('name')
                quantity = item.get('quantity', 1)
                price = item.get('price', 0.0)
                
                logger.info(f"[AGE VERIFICATION] Adding item {product_id} with price {price}")
                
                # Create basket item
                basket_item = BasketItem.objects.create(
                    basket=basket,
                    product_id=product_id,
                    product_name=product_name,
                    quantity=quantity,
                    price=price
                )
                
                # Publish verified item added event
                event_producer.publish(settings.KAFKA_TOPIC, {
                    'event_type': 'verified.item.added',
                    'timestamp': datetime.now().isoformat(),
                    'basket_id': basket_id,
                    'product_id': product_id,
                    'product_name': product_name,
                    'quantity': quantity,
                    'price': price,
                    'item_id': str(basket_item.id)
                })
                
                logger.info(f"[AGE VERIFICATION] Successfully added {product_name} with price ${price}")
                
        except Exception as e:
            logger.error(f"[AGE VERIFICATION] Failed to add verified items: {e}")