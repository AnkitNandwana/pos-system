import strawberry
from strawberry import auto
from .models import Customer


@strawberry.django.type(Customer)
class CustomerType:
    id: auto
    customer_id: auto
    identifier: auto
    first_name: auto
    last_name: auto
    email: auto
    phone: auto
    loyalty_points: auto
    tier: auto
    total_purchases: auto
    last_purchase_date: auto
    created_at: auto
