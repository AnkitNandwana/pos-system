import strawberry
import asyncio
from typing import AsyncGenerator, List, Optional
from events.consumer import EventConsumer
from django.conf import settings
import json


@strawberry.type
class RestrictedItem:
    product_id: str
    name: str
    minimum_age: int
    category: str


@strawberry.type
class BasketEvent:
    event_type: str
    basket_id: str
    product_id: Optional[str] = None
    message: Optional[str] = None


@strawberry.type
class AgeVerificationEvent:
    event_type: str
    basket_id: str
    restricted_items: List[RestrictedItem] = strawberry.field(default_factory=list)
    minimum_age: int = 18
    customer_age: Optional[int] = None
    verification_method: Optional[str] = None
    verifier_id: Optional[int] = None
    reason: Optional[str] = None
    action_required: Optional[str] = None


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def age_verification_events(self, basket_id: str) -> AsyncGenerator[AgeVerificationEvent, None]:
        """Subscribe to age verification events for a specific basket"""
        consumer = EventConsumer()
        
        async for event in consumer.subscribe_to_events([
            'age.verification.required',
            'age.verification.completed', 
            'age.verification.failed',
            'age.verification.cancelled'
        ]):
            if event.get('basket_id') == basket_id:
                # Parse restricted items from event data
                restricted_items = []
                if event.get('restricted_items'):
                    for item in event.get('restricted_items', []):
                        restricted_items.append(RestrictedItem(
                            product_id=item.get('productId', ''),
                            name=item.get('name', ''),
                            minimum_age=item.get('minimum_age', 18),
                            category=item.get('category', '')
                        ))
                
                yield AgeVerificationEvent(
                    event_type=event.get('event_type', ''),
                    basket_id=event.get('basket_id', ''),
                    restricted_items=restricted_items,
                    minimum_age=event.get('minimum_age', 18),
                    customer_age=event.get('customer_age'),
                    verification_method=event.get('verification_method'),
                    verifier_id=event.get('verifier_id'),
                    reason=event.get('reason'),
                    action_required=event.get('action_required')
                )
    
    @strawberry.subscription
    async def basket_events(self, basket_id: str) -> AsyncGenerator[BasketEvent, None]:
        """Subscribe to all basket-related events"""
        consumer = EventConsumer()
        
        async for event in consumer.subscribe_to_events([
            'item.added',
            'item.removed', 
            'verified.item.added',
            'age.verification.required',
            'age.verification.completed',
            'age.verification.failed'
        ]):
            if event.get('basket_id') == basket_id:
                yield BasketEvent(
                    event_type=event.get('event_type', ''),
                    basket_id=event.get('basket_id', ''),
                    product_id=event.get('product_id'),
                    message=event.get('message')
                )