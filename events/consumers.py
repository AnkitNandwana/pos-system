import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from plugins.purchase_recommender.models import Recommendation


class RecommendationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.basket_id = self.scope['url_route']['kwargs']['basket_id']
        self.room_group_name = f'recommendations_{self.basket_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def recommendation_message(self, event):
        recommendations = event['recommendations']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'recommendations',
            'recommendations': recommendations
        }))

    @database_sync_to_async
    def get_pending_recommendations(self):
        return list(Recommendation.objects.filter(
            basket_id=self.basket_id,
            status='PENDING'
        ).values(
            'id', 'recommended_product_id', 'recommended_product_name',
            'recommended_price', 'reason', 'status'
        ))