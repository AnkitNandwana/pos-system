from .models import PluginConfiguration
import logging

logger = logging.getLogger(__name__)


class PluginRegistry:
    _instance = None
    _plugins = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, plugin_class):
        """Register a plugin"""
        self._plugins[plugin_class.name] = plugin_class
        logger.info(f"Registered plugin: {plugin_class.name}")
    
    def get_enabled_plugins(self):
        """Get all enabled plugins with their configurations"""
        enabled_configs = PluginConfiguration.objects.filter(enabled=True)
        enabled_plugins = []
        
        for config in enabled_configs:
            plugin_class = self._plugins.get(config.name)
            if plugin_class:
                plugin_instance = plugin_class(config=config.config)
                enabled_plugins.append(plugin_instance)
        
        return enabled_plugins
    
    def route_event(self, event_type, event_data):
        """Route event to all enabled plugins that can handle it"""
        enabled_plugins = self.get_enabled_plugins()

        logger.info(f"Routing {event_type} to {len(enabled_plugins)} enabled plugins")
        
        for plugin in enabled_plugins:
            logger.info(f"Checking plugin {plugin.name} for {event_type} - can_handle: {plugin.can_handle(event_type)}")
            if plugin.can_handle(event_type):
                try:
                    plugin.handle_event(event_type, event_data)
                    logger.info(f"Plugin {plugin.name} handled event {event_type}")
                except Exception as e:
                    logger.error(f"Plugin {plugin.name} failed to handle event: {e}")


# Singleton instance
plugin_registry = PluginRegistry()
