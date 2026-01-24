import strawberry
from typing import Optional, List
from .models import Customer
from .types import CustomerType


@strawberry.type
class CustomerQueries:
    @strawberry.field
    def customer(self, customer_id: str) -> Optional[CustomerType]:
        try:
            return Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return None
    
    @strawberry.field
    def customer_by_identifier(self, identifier: str) -> Optional[CustomerType]:
        try:
            return Customer.objects.get(identifier=identifier)
        except Customer.DoesNotExist:
            return None
    
    @strawberry.field
    def all_customers(self) -> List[CustomerType]:
        return list(Customer.objects.all().order_by('-created_at'))
