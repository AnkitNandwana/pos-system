import strawberry
from typing import List
from django.db.models import Q
from .models import Product
from .types import ProductType


@strawberry.type
class ProductQueries:
    @strawberry.field
    def products(self) -> List[ProductType]:
        return list(Product.objects.all())
    
    @strawberry.field
    def search_products(self, query: str) -> List[ProductType]:
        return list(Product.objects.filter(
            Q(name__icontains=query) | 
            Q(product_id__icontains=query) |
            Q(category__icontains=query)
        )[:20])
    
    @strawberry.field
    def product(self, product_id: str) -> ProductType:
        return Product.objects.get(product_id=product_id)