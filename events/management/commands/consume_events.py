from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
from django.conf import settings
from plugins.registry import plugin_registry
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
        
        # Create Kafka consumer
        consumer = KafkaConsumer(
            settings.KAFKA_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='pos-consumer-group-v2',
            auto_offset_reset='latest'
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
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Shutting down consumer...'))
        finally:
            consumer.close()
