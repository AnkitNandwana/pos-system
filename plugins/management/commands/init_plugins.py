from django.core.management.base import BaseCommand
from plugins.models import PluginConfiguration
from plugins.registry import plugin_registry


class Command(BaseCommand):
    help = 'Initialize plugin configurations in database'
    
    def handle(self, *args, **options):
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
        
        self.stdout.write(
            self.style.SUCCESS('Plugin initialization completed')
        )