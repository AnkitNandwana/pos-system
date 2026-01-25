import strawberry
from strawberry import auto
from typing import List, Optional
from .models import Basket, BasketItem
from employees.types import EmployeeType
from customers.types import CustomerType


@strawberry.django.type(Basket)
class BasketType:
    id: auto
    basket_id: auto
    customer_id: auto
    status: auto
    created_at: auto
    
    @strawberry.field
    def employee(self) -> EmployeeType:
        return self.employee
    
    @strawberry.field
    def customer(self) -> Optional[CustomerType]:
        if self.customer_id:
            from customers.models import Customer
            try:
                return Customer.objects.get(customer_id=self.customer_id)
            except Customer.DoesNotExist:
                return None
        return None
    
    @strawberry.field
    def items(self) -> List['BasketItemType']:
        return list(self.items.all())
    
    @strawberry.field
    def total_amount(self) -> float:
        return float(sum(item.price * item.quantity for item in self.items.all()))


@strawberry.django.type(BasketItem)
class BasketItemType:
    id: auto
    product_id: auto
    product_name: auto
    quantity: auto
    price: auto
    added_at: auto
