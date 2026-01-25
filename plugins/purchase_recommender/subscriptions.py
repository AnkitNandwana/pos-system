import strawberry
from typing import List, AsyncGenerator
from .types import RecommendationType
from events.consumer import EventConsumer
import logging

logger = logging.getLogger(__name__)


@strawberry.type
class RecommendationSubscriptions:
    @strawberry.subscription
    async def recommendations(self, basket_id: str) -> AsyncGenerator[List[RecommendationType], None]:
        """Real-time subscription for recommendations"""
        consumer = EventConsumer()
        
        async for event in consumer.subscribe_to_events(['RECOMMENDATION_SUGGESTED']):
            if event.get('basket_id') == basket_id:
                # Convert recommendations to GraphQL types
                recommendations = []
                for rec in event.get('recommendations', []):
                    recommendations.append(RecommendationType(
                        id=0,  # Temporary ID for new recommendations
                        recommended_product_id=rec['product_id'],
                        recommended_product_name=rec['name'],
                        recommended_price=float(rec['price']),
                        reason='Frequently bought together',
                        status='PENDING'
                    ))
                
                logger.info(f"Sending {len(recommendations)} recommendations for basket {basket_id}")
                yield recommendations