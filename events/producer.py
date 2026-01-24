from kafka import KafkaProducer
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class EventProducer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.producer = None
        return cls._instance
    
    def _get_producer(self):
        """Lazy initialization of Kafka producer"""
        if self.producer is None:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        return self.producer
    
    def publish(self, topic, event_data):
        """Publish event to Kafka topic"""
        try:
            producer = self._get_producer()
            future = producer.send(topic, event_data)
            producer.flush()
            logger.info(f"Published event to {topic}: {event_data}")
            return future
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    def close(self):
        """Close producer connection"""
        if self.producer:
            self.producer.close()


# Singleton instance
event_producer = EventProducer()
