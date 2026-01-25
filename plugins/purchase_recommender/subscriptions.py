import strawberry
from typing import List, AsyncGenerator
from .types import RecommendationType
import asyncio
import json


@strawberry.type
class RecommendationSubscriptions:
    @strawberry.subscription
    async def recommendations(self, basket_id: str) -> AsyncGenerator[List[RecommendationType], None]:
        """Real-time subscription for recommendations"""
        # This is a simplified implementation
        # In production, you'd connect to the WebSocket channel layer
        while True:
            # Fetch current recommendations
            from .models import Recommendation
            recommendations = list(Recommendation.objects.filter(
                basket_id=basket_id,
                status='PENDING'
            ))
            
            yield recommendations
            await asyncio.sleep(1)  # Check every second