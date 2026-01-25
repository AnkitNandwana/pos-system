import strawberry
from typing import List
from .models import PluginConfiguration
from .types import Plugin
from .registry import plugin_registry
import json


@strawberry.type
class PluginQueries:
    @strawberry.field
    def plugins(self) -> List[Plugin]:
        plugins = []
        
        # Get all plugin configurations from database
        plugin_configs = PluginConfiguration.objects.all()
        config_dict = {config.name: config for config in plugin_configs}
        
        # Get all registered plugins
        for plugin_name, plugin_class in plugin_registry._plugins.items():
            config = config_dict.get(plugin_name)
            
            # Get supported events from plugin class
            supported_events = []
            if hasattr(plugin_class, 'get_supported_events'):
                try:
                    plugin_instance = plugin_class()
                    supported_events = plugin_instance.get_supported_events()
                except:
                    supported_events = []
            
            plugins.append(Plugin(
                id=str(config.id if config else 0),
                name=plugin_name,
                enabled=config.enabled if config else False,
                description=config.description if config else getattr(plugin_class, 'description', ''),
                config=json.dumps(config.config) if config and config.config else '{}',
                supported_events=supported_events
            ))
        
        return plugins