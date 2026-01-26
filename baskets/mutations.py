import strawberry
import uuid
from django.utils import timezone
from typing import Optional
from .models import Basket, BasketItem
from .types import BasketType, BasketItemType
from employees.models import Employee
from products.models import Product
from events.producer import event_producer
from django.conf import settings


@strawberry.type
class BasketMutations:
    @strawberry.mutation
    def start_basket(self, employee_id: int, terminal_id: str, customer_identifier: Optional[str] = None) -> BasketType:
        employee = Employee.objects.get(id=employee_id)
        basket = Basket.objects.create(
            basket_id=f"basket_{uuid.uuid4().hex[:8]}",
            employee=employee,
            customer_id=customer_identifier
        )
        
        # Publish basket started event
        event_producer.publish(settings.KAFKA_TOPIC, {
            'event_type': 'basket.started',
            'timestamp': timezone.now().isoformat(),
            'employee_id': employee_id,
            'basket_id': basket.basket_id,
            'terminal_id': terminal_id,
            'customer_identifier': customer_identifier
        })
        
        return basket
    
    @strawberry.mutation
    def add_item(
        self, 
        basket_id: str, 
        product_id: str, 
        product_name: str,
        quantity: int, 
        price: float
    ) -> Optional[BasketItemType]:
        import logging
        logger = logging.getLogger(__name__)
        
        basket = Basket.objects.get(basket_id=basket_id)
        logger.info(f"[ADD_ITEM] Adding item {product_id} to basket {basket_id}")
        logger.info(f"[ADD_ITEM] Received price: {price}")
        logger.info(f"[ADD_ITEM] Received price: {price}")
        
        # Check if product requires age verification
        try:
            product = Product.objects.get(product_id=product_id)
            logger.info(f"[ADD_ITEM] Product found: {product.name}, age_restricted: {product.age_restricted}")
            
            if product.age_restricted:
                logger.info(f"[ADD_ITEM] Age-restricted item detected, publishing event")
                
                # Publish age verification required event
                event_producer.publish(settings.KAFKA_TOPIC, {
                    'event_type': 'item.added',
                    'timestamp': timezone.now().isoformat(),
                    'basket_id': basket_id,
                    'product_id': product_id,
                    'product_name': product_name,
                    'quantity': quantity,
                    'price': price,
                    'employee_id': basket.employee.id,
                    'age_restricted': True
                })
                
                logger.info(f"[ADD_ITEM] Event published for age-restricted item with price: {price}")
                
                # Add item directly to basket (plugin will handle verification separately)
                item = BasketItem.objects.create(
                    basket=basket,
                    product_id=product_id,
                    product_name=product_name,
                    quantity=quantity,
                    price=price
                )
                
                logger.info(f"[ADD_ITEM] Age-restricted item added to basket with price: {price}")
                return item
                
        except Product.DoesNotExist:
            logger.warning(f"[ADD_ITEM] Product {product_id} not found")
        
        # Add item normally if no age restriction
        logger.info(f"[ADD_ITEM] Adding normal item to database")
        item = BasketItem.objects.create(
            basket=basket,
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            price=price
        )
        
        # Publish normal item added event for recommendations
        event_producer.publish(settings.KAFKA_TOPIC, {
            'event_type': 'item.added',
            'timestamp': timezone.now().isoformat(),
            'basket_id': basket_id,
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
            'price': price,
            'employee_id': basket.employee.id,
            'age_restricted': False
        })
        
        logger.info(f"[ADD_ITEM] Normal item added successfully")
        return item
    
    @strawberry.mutation
    def remove_item(self, basket_id: str, item_id: str) -> bool:
        try:
            basket = Basket.objects.get(basket_id=basket_id)
            item = BasketItem.objects.get(id=item_id, basket=basket)
            
            # Publish event before deletion
            event_producer.publish(settings.KAFKA_TOPIC, {
                'event_type': 'item.removed',
                'timestamp': timezone.now().isoformat(),
                'basket_id': basket_id,
                'product_id': item.product_id,
                'item_id': item_id
            })
            
            item.delete()
            return True
        except (Basket.DoesNotExist, BasketItem.DoesNotExist):
            return False
    
    @strawberry.mutation
    def update_quantity(self, basket_id: str, item_id: str, quantity: int) -> BasketItemType:
        basket = Basket.objects.get(basket_id=basket_id)
        item = BasketItem.objects.get(id=item_id, basket=basket)
        item.quantity = quantity
        item.save()
        
        # Publish event
        event_producer.publish(settings.KAFKA_TOPIC, {
            'event_type': 'ITEM_QUANTITY_UPDATED',
            'timestamp': timezone.now().isoformat(),
            'basket_id': basket_id,
            'item_id': item_id,
            'new_quantity': quantity
        })
        
        return item
    
    @strawberry.mutation
    def finalize_basket(self, basket_id: str) -> BasketType:
        basket = Basket.objects.get(basket_id=basket_id)
        basket.status = 'FINALIZED'
        basket.save()
        
        # Publish event
        event_producer.publish(settings.KAFKA_TOPIC, {
            'event_type': 'BASKET_FINALIZED',
            'timestamp': timezone.now().isoformat(),
            'basket_id': basket_id
        })
        
        return basket
    @strawberry.mutation
    def verify_age(
        self, 
        basket_id: str, 
        verifier_employee_id: int,
        customer_age: int,
        verification_method: str = "MANUAL_CHECK"
    ) -> bool:
        """Verify customer age for age-restricted items"""
        try:
            # Publish age verification event
            event_producer.publish(settings.KAFKA_TOPIC, {
                'event_type': 'age.verified',
                'timestamp': timezone.now().isoformat(),
                'basket_id': basket_id,
                'verifier_employee_id': verifier_employee_id,
                'customer_age': customer_age,
                'verification_method': verification_method
            })
            return True
        except Exception:
            return False
    
    @strawberry.mutation
    def add_verified_item(
        self,
        basket_id: str,
        product_id: str,
        product_name: str,
        quantity: int,
        price: float
    ) -> BasketItemType:
        """Add age-restricted item after verification"""
        basket = Basket.objects.get(basket_id=basket_id)
        item = BasketItem.objects.create(
            basket=basket,
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            price=price
        )
        
        # Publish verified item added event
        event_producer.publish(settings.KAFKA_TOPIC, {
            'event_type': 'verified.item.added',
            'timestamp': timezone.now().isoformat(),
            'basket_id': basket_id,
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
            'price': price
        })
        
        return item
    
    @strawberry.mutation
    def cancel_age_verification(self, basket_id: str, employee_id: int) -> bool:
        """Cancel age verification - reject restricted items"""
        try:
            # Publish age verification cancelled event
            event_producer.publish(settings.KAFKA_TOPIC, {
                'event_type': 'age.verification.cancelled',
                'timestamp': timezone.now().isoformat(),
                'basket_id': basket_id,
                'employee_id': employee_id,
                'reason': 'VERIFICATION_CANCELLED'
            })
            return True
        except Exception:
            return False
    
    @strawberry.mutation
    def process_payment(
        self,
        basket_id: str,
        terminal_id: str,
        employee_id: int,
        total_amount: float,
        payment_method: str
    ) -> bool:
        """Process dummy payment and complete basket"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            basket = Basket.objects.get(basket_id=basket_id)
            
            # Log payment details (dummy payment - no real processing)
            logger.info(f"[PAYMENT] Processing payment for basket {basket_id}")
            logger.info(f"[PAYMENT] Amount: ${total_amount}, Method: {payment_method}")
            logger.info(f"[PAYMENT] Terminal: {terminal_id}, Employee: {employee_id}")
            
            # Update basket status to PAID (completed)
            basket.status = 'PAID'
            basket.save()
            
            # Publish payment completed event
            event_producer.publish(settings.KAFKA_TOPIC, {
                'event_type': 'payment.completed',
                'timestamp': timezone.now().isoformat(),
                'basket_id': basket_id,
                'terminal_id': terminal_id,
                'employee_id': employee_id,
                'total_amount': total_amount,
                'payment_method': payment_method
            })
            
            logger.info(f"[PAYMENT] Payment completed successfully for basket {basket_id}")
            return True
            
        except Basket.DoesNotExist:
            logger.error(f"[PAYMENT] Basket {basket_id} not found")
            return False
        except Exception as e:
            logger.error(f"[PAYMENT] Payment failed: {str(e)}")
            return False