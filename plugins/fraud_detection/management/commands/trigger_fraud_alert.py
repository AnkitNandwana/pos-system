from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
import uuid


class Command(BaseCommand):
    help = 'Manually trigger a fraud alert for testing'

    def add_arguments(self, parser):
        parser.add_argument('terminal_id', type=str, help='Terminal ID to send alert to')
        parser.add_argument('--severity', type=str, default='HIGH', 
                          choices=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
                          help='Alert severity level')

    def handle(self, *args, **options):
        terminal_id = options['terminal_id']
        severity = options['severity']
        channel_layer = get_channel_layer()
        
        alert_id = str(uuid.uuid4())
        
        self.stdout.write(f'Sending fraud alert to terminal: {terminal_id}')
        
        async_to_sync(channel_layer.group_send)(
            f'fraud_alerts_{terminal_id}',
            {
                'type': 'fraud_alert',
                'alert_id': alert_id,
                'rule_id': 'test_manual_alert',
                'severity': severity,
                'details': {
                    'rule_name': 'Manual Test Alert',
                    'threshold': 100,
                    'actual_value': 150,
                    'description': 'This is a manually triggered test alert'
                },
                'timestamp': timezone.now().isoformat()
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Fraud alert sent to terminal {terminal_id} with severity {severity}')
        )