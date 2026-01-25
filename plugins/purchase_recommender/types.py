import strawberry
from strawberry import auto
from .models import Recommendation


@strawberry.django.type(Recommendation)
class RecommendationType:
    id: auto
    basket_id: auto
    source_product_id: auto
    recommended_product_id: auto
    recommended_product_name: auto
    recommended_price: auto
    reason: auto
    status: auto
    recommended_at: auto
    was_accepted: auto
