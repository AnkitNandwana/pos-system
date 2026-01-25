import asyncio
import json
from kafka import KafkaConsumer
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EventConsumer:
    def __init__(self):
        self.consumer = None
    
    async def subscribe_to_events(self, event_types):
        """Subscribe to specific event types and yield matching events"""
        try:
            # Create Kafka consumer
            consumer = KafkaConsumer(
                settings.KAFKA_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True
            )
            
            logger.info(f"Subscribed to events: {event_types}")
            
            # Poll for messages
            while True:
                message_pack = consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_pack.items():
                    for message in messages:
                        event = message.value
                        event_type = event.get('event_type')
                        
                        if event_type in event_types:
                            yield event
                
                # Allow other coroutines to run
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Event consumer error: {e}")
        finally:
            if consumer:
                consumer.close()