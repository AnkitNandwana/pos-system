import strawberry
from strawberry import auto
from typing import List
from .models import Basket, BasketItem


@strawberry.django.type(Basket)
class BasketType:
    id: auto
    basket_id: auto
    customer_id: auto
    status: auto
    created_at: auto
    
    @strawberry.field
    def items(self) -> List['BasketItemType']:
        return self.items.all()


@strawberry.django.type(BasketItem)
class BasketItemType:
    id: auto
    product_id: auto
    product_name: auto
    quantity: auto
    price: auto
    added_at: auto
