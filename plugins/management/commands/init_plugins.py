from django.core.management.base import BaseCommand
from plugins.models import PluginConfiguration
from plugins.registry import plugin_registry
from plugins.fraud_detection.models import FraudRule
from plugins.age_verification.models import AgeVerificationLog


class Command(BaseCommand):
    help = 'Initialize plugin configurations and seed plugin data'
    
    def handle(self, *args, **options):
        # Initialize plugin configurations
        for plugin_name, plugin_class in plugin_registry._plugins.items():
            config, created = PluginConfiguration.objects.get_or_create(
                name=plugin_name,
                defaults={
                    'enabled': True,
                    'description': getattr(plugin_class, 'description', f'{plugin_name} plugin'),
                    'config': {}
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created configuration for plugin: {plugin_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Configuration already exists for plugin: {plugin_name}')
                )
        
        # Seed fraud detection rules
        fraud_rules = [
            {
                'rule_name': 'rapid_items',
                'description': 'Detect rapid item additions',
                'rule_type': 'RAPID_ITEMS',
                'threshold_value': 5.0,
                'time_window_seconds': 30,
                'is_active': True
            },
            {
                'rule_name': 'high_value_transaction',
                'description': 'Detect high value transactions',
                'rule_type': 'HIGH_VALUE',
                'threshold_value': 500.0,
                'time_window_seconds': 0,
                'is_active': True
            },
            {
                'rule_name': 'suspicious_pattern',
                'description': 'Detect suspicious purchase patterns',
                'rule_type': 'PATTERN',
                'threshold_value': 3.0,
                'time_window_seconds': 300,
                'is_active': True
            }
        ]
        
        fraud_created = 0
        for rule_data in fraud_rules:
            rule, created = FraudRule.objects.get_or_create(
                rule_name=rule_data['rule_name'],
                defaults=rule_data
            )
            if created:
                fraud_created += 1
                self.stdout.write(f"Created fraud rule: {rule.rule_name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Plugin initialization completed - {fraud_created} fraud rules created')
        )