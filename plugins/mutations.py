import strawberry
from typing import List, Optional
from .models import PluginConfiguration
from .types import Plugin
from .registry import plugin_registry
import json


@strawberry.type
class PluginMutations:
    @strawberry.mutation
    def update_plugin(
        self,
        id: strawberry.ID,
        enabled: Optional[bool] = None,
        config: Optional[str] = None,
        supported_events: Optional[List[str]] = None
    ) -> Plugin:
        # Get plugin configuration
        try:
            plugin_config = PluginConfiguration.objects.get(id=id)
        except PluginConfiguration.DoesNotExist:
            raise Exception(f"Plugin with id {id} not found")
        
        # Update fields if provided
        if enabled is not None:
            plugin_config.enabled = enabled
        
        if config is not None:
            try:
                plugin_config.config = json.loads(config)
            except json.JSONDecodeError:
                raise Exception("Invalid JSON configuration")
        
        plugin_config.save()
        
        # Get supported events from plugin class
        plugin_class = plugin_registry._plugins.get(plugin_config.name)
        current_supported_events = []
        if plugin_class and hasattr(plugin_class, 'get_supported_events'):
            try:
                plugin_instance = plugin_class()
                current_supported_events = plugin_instance.get_supported_events()
            except:
                current_supported_events = []
        
        return Plugin(
            id=str(plugin_config.id),
            name=plugin_config.name,
            enabled=plugin_config.enabled,
            description=plugin_config.description,
            config=json.dumps(plugin_config.config),
            supported_events=current_supported_events
        )