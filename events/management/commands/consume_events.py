from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
from django.conf import settings
from plugins.registry import plugin_registry
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import logging
import sys

# Configure logging to display INFO level messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Consume events from Kafka and route to plugins'
    
    def handle(self, *args, **options):
        # Register plugins (lazy import to avoid circular dependency)
        from plugins.employee_time_tracker.plugin import EmployeeTimeTrackerPlugin
        from plugins.purchase_recommender.plugin import PurchaseRecommenderPlugin
        from plugins.customer_lookup.plugin import CustomerLookupPlugin
        from plugins.fraud_detection.plugin import FraudDetectionPlugin
        from plugins.age_verification.plugin import AgeVerificationPlugin
        
        plugin_registry.register(EmployeeTimeTrackerPlugin)
        plugin_registry.register(PurchaseRecommenderPlugin)
        plugin_registry.register(CustomerLookupPlugin)
        plugin_registry.register(FraudDetectionPlugin)
        plugin_registry.register(AgeVerificationPlugin)
        
        # Get channel layer for WebSocket communication
        channel_layer = get_channel_layer()
        
        # Create Kafka consumer
        consumer = KafkaConsumer(
            settings.KAFKA_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='pos-consumer-group-1',
            auto_offset_reset='latest',
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000
        )
        
        self.stdout.write(self.style.SUCCESS('Kafka consumer started...'))
        
        try:
            for message in consumer:
                event_data = message.value
                event_type = event_data.get('event_type')
                employee_id = event_data.get('employee_id', 'N/A')
                terminal_id = event_data.get('terminal_id', 'N/A')
                
                self.stdout.write(f"\n{'='*60}")
                self.stdout.write(f"Event: {event_type}")
                self.stdout.write(f"Employee ID: {employee_id} | Terminal ID: {terminal_id}")
                self.stdout.write(f"{'='*60}")
                
                # Route event to plugins
                plugin_registry.route_event(event_type, event_data)
                
                # Handle recommendation events for real-time updates
                if event_type == 'RECOMMENDATION_SUGGESTED':
                    basket_id = event_data.get('basket_id')
                    if basket_id and channel_layer:
                        # Get fresh recommendations from database
                        from plugins.purchase_recommender.models import Recommendation
                        recommendations = list(Recommendation.objects.filter(
                            basket_id=basket_id,
                            status='PENDING'
                        ).values(
                            'id', 'recommended_product_id', 'recommended_product_name',
                            'recommended_price', 'reason', 'status'
                        ))
                        
                        # Send to WebSocket group
                        formatted_recommendations = [{
                            'id': rec['id'],
                            'recommendedProductId': rec['recommended_product_id'],
                            'recommendedProductName': rec['recommended_product_name'],
                            'recommendedPrice': float(rec['recommended_price']),
                            'reason': rec['reason'],
                            'status': rec['status']
                        } for rec in recommendations]
                        
                        async_to_sync(channel_layer.group_send)(
                            f'recommendations_{basket_id}',
                            {
                                'type': 'recommendation_message',
                                'recommendations': formatted_recommendations
                            }
                        )
                        
                        self.stdout.write(f"Sent {len(recommendations)} recommendations to WebSocket group")
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Shutting down consumer...'))
        finally:
            consumer.close()
