import strawberry
import uuid
from django.utils import timezone
from .models import Basket, BasketItem
from .types import BasketType, BasketItemType
from employees.models import Employee
from events.producer import event_producer
from django.conf import settings


@strawberry.type
class BasketMutations:
    @strawberry.mutation
    def start_basket(self, employee_id: int, terminal_id: str) -> BasketType:
        employee = Employee.objects.get(id=employee_id)
        basket = Basket.objects.create(
            basket_id=f"basket_{uuid.uuid4().hex[:8]}",
            employee=employee
        )
        
        # Publish event
        event_producer.publish(settings.KAFKA_TOPIC, {
            'event_type': 'BASKET_STARTED',
            'timestamp': timezone.now().isoformat(),
            'employee_id': employee_id,
            'basket_id': basket.basket_id,
            'terminal_id': terminal_id
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
    ) -> BasketItemType:
        basket = Basket.objects.get(basket_id=basket_id)
        item = BasketItem.objects.create(
            basket=basket,
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            price=price
        )
        
        # Publish event
        event_producer.publish(settings.KAFKA_TOPIC, {
            'event_type': 'ITEM_ADDED',
            'timestamp': timezone.now().isoformat(),
            'basket_id': basket_id,
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
            'price': price
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
