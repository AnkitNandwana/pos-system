import strawberry
from typing import List
from .models import Recommendation
from .types import RecommendationType


@strawberry.type
class RecommendationQueries:
    @strawberry.field
    def recommendations(self, basket_id: str) -> List[RecommendationType]:
        return list(Recommendation.objects.filter(
            basket_id=basket_id, 
            status='PENDING'
        ).order_by('-recommended_at'))
    
    @strawberry.field
    def pending_recommendations(self, basket_id: str) -> List[RecommendationType]:
        return list(Recommendation.objects.filter(
            basket_id=basket_id,
            status='PENDING'
        ).order_by('-recommended_at'))
