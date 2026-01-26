import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from plugins.fraud_detection.models import FraudAlert


class FraudAlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.terminal_id = self.scope['url_route']['kwargs']['terminal_id']
        self.room_group_name = f'fraud_alerts_{self.terminal_id}'

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
    async def fraud_alert(self, event):
        # Send fraud alert to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'fraud_alert',
            'alert_id': event['alert_id'],
            'rule_id': event['rule_id'],
            'severity': event['severity'],
            'details': event['details'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def acknowledge_alert(self, alert_id):
        try:
            alert = FraudAlert.objects.get(alert_id=alert_id)
            alert.acknowledged = True
            alert.save()
            return True
        except FraudAlert.DoesNotExist:
            return False