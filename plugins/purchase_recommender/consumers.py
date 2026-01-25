import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from plugins.purchase_recommender.models import Recommendation


class RecommendationWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.basket_id = self.scope['url_route']['kwargs']['basket_id']
        self.room_group_name = f'recommendations_{self.basket_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send test message on connect
        await self.send(text_data=json.dumps({
            'type': 'test',
            'message': f'Connected to recommendations for basket {self.basket_id}'
        }))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def recommendation_message(self, event):
        """Handle recommendation messages from the group"""
        recommendations = event['recommendations']
        
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