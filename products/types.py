import strawberry
from strawberry import auto
from .models import Product


@strawberry.django.type(Product)
class ProductType:
    id: auto
    product_id: auto
    name: auto
    price: auto
    category: auto
    age_restricted: auto
    minimum_age: auto
    age_restriction_category: auto
    created_at: auto