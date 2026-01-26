import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from terminals.models import Terminal


class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.terminal_id = self.scope['url_route']['kwargs']['terminal_id']
        self.room_group_name = f'session_{self.terminal_id}'

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
    async def session_terminated(self, event):
        # Send session terminated message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'session_terminated',
            'message': event['message'],
            'reason': event.get('reason', 'auto_logout'),
            'timestamp': event.get('timestamp')
        }))

    @database_sync_to_async
    def get_terminal_status(self):
        try:
            terminal = Terminal.objects.get(terminal_id=self.terminal_id)
            return terminal.is_active
        except Terminal.DoesNotExist:
            return False