from django.core.management.base import BaseCommand
from plugins.fraud_detection.models import FraudRule
from plugins.models import PluginConfiguration


class Command(BaseCommand):
    help = 'Setup fraud detection plugin with default rules'
    
    def handle(self, *args, **options):
        # Create plugin configuration
        config, created = PluginConfiguration.objects.get_or_create(
            name='fraud_detection',
            defaults={
                'enabled': True,
                'description': 'Detects fraudulent activities in POS transactions',
                'config': {}
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created fraud_detection plugin configuration'))
        else:
            self.stdout.write('Plugin configuration already exists')
        
        # Create default fraud rules
        rules = [
            {
                'rule_id': 'multiple_terminals',
                'name': 'Employee on Multiple Terminals',
                'description': 'Detects when employee logs into multiple terminals within time window',
                'severity': 'HIGH',
                'time_window': 300,  # 5 minutes
                'threshold': 2
            },
            {
                'rule_id': 'rapid_items',
                'name': 'Rapid Item Addition',
                'description': 'Detects when items are added too quickly to basket',
                'severity': 'MEDIUM',
                'time_window': 60,  # 1 minute
                'threshold': 10
            },
            {
                'rule_id': 'high_value_payment',
                'name': 'High Value Payment in Short Session',
                'description': 'Detects high-value payments within short login sessions',
                'severity': 'HIGH',
                'time_window': 600,  # 10 minutes
                'threshold': 1000  # $1000
            },
            {
                'rule_id': 'anonymous_payment',
                'name': 'Anonymous High-Value Payment',
                'description': 'Detects high-value payments without customer identification',
                'severity': 'MEDIUM',
                'time_window': 0,
                'threshold': 500  # $500
            },
            {
                'rule_id': 'rapid_checkout',
                'name': 'Rapid Basket Checkout',
                'description': 'Detects baskets completed too quickly after creation',
                'severity': 'LOW',
                'time_window': 30,  # 30 seconds
                'threshold': 30
            }
        ]
        
        created_count = 0
        for rule_data in rules:
            rule, created = FraudRule.objects.get_or_create(
                rule_id=rule_data['rule_id'],
                defaults=rule_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created rule: {rule.name}")
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Created {created_count} fraud rules'))
        else:
            self.stdout.write('All fraud rules already exist')
        
        self.stdout.write(self.style.SUCCESS('Fraud detection setup complete!'))