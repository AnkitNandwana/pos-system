import strawberry
from typing import List, Optional
from .models import Basket
from .types import BasketType


@strawberry.type
class BasketQueries:
    @strawberry.field
    def basket(self, basket_id: str) -> Optional[BasketType]:
        try:
            return Basket.objects.get(basket_id=basket_id)
        except Basket.DoesNotExist:
            return None
    
    @strawberry.field
    def basket_details(self, basket_id: str) -> Optional[BasketType]:
        try:
            return Basket.objects.get(basket_id=basket_id)
        except Basket.DoesNotExist:
            return None
    
    @strawberry.field
    def active_baskets(self, employee_id: int) -> List[BasketType]:
        return list(Basket.objects.filter(employee_id=employee_id, status='ACTIVE'))
