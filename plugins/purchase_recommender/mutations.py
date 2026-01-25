import strawberry
from django.utils import timezone
from .models import Recommendation
from .types import RecommendationType
from baskets.models import BasketItem, Basket
from events.producer import event_producer
from django.conf import settings


@strawberry.type
class RecommendationResponse:
    success: bool
    message: str


@strawberry.type
class RecommendationMutations:
    @strawberry.mutation
    def accept_recommendation(self, recommendation_id: int, basket_id: str) -> RecommendationResponse:
        try:
            recommendation = Recommendation.objects.get(id=recommendation_id)
            recommendation.status = 'ACCEPTED'
            recommendation.was_accepted = True
            recommendation.save()
            
            # Add item to basket
            basket = Basket.objects.get(basket_id=basket_id)
            BasketItem.objects.create(
                basket=basket,
                product_id=recommendation.recommended_product_id,
                product_name=recommendation.recommended_product_name,
                quantity=1,
                price=recommendation.recommended_price or 0
            )
            
            # Publish events
            event_producer.publish(settings.KAFKA_TOPIC, {
                'event_type': 'RECOMMENDATION_ACCEPTED',
                'timestamp': timezone.now().isoformat(),
                'basket_id': basket_id,
                'recommendation_id': recommendation_id,
                'product_id': recommendation.recommended_product_id
            })
            
            event_producer.publish(settings.KAFKA_TOPIC, {
                'event_type': 'ITEM_ADDED',
                'timestamp': timezone.now().isoformat(),
                'basket_id': basket_id,
                'product_id': recommendation.recommended_product_id,
                'product_name': recommendation.recommended_product_name,
                'quantity': 1,
                'price': float(recommendation.recommended_price or 0)
            })
            
            return RecommendationResponse(success=True, message="Recommendation accepted")
        except Exception as e:
            return RecommendationResponse(success=False, message=str(e))
    
    @strawberry.mutation
    def reject_recommendation(self, recommendation_id: int) -> RecommendationResponse:
        try:
            recommendation = Recommendation.objects.get(id=recommendation_id)
            recommendation.status = 'REJECTED'
            recommendation.was_accepted = False
            recommendation.save()
            
            # Publish event
            event_producer.publish(settings.KAFKA_TOPIC, {
                'event_type': 'RECOMMENDATION_REJECTED',
                'timestamp': timezone.now().isoformat(),
                'basket_id': recommendation.basket_id,
                'recommendation_id': recommendation_id
            })
            
            return RecommendationResponse(success=True, message="Recommendation rejected")
        except Exception as e:
            return RecommendationResponse(success=False, message=str(e))