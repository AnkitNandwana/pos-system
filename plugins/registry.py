from .models import PluginConfiguration
import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)


class PluginRegistry:
    _instance = None
    _plugins = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._processed_events = defaultdict(set)
            cls._instance._cleanup_interval = 300  # 5 minutes
            cls._instance._last_cleanup = time.time()
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
        # Create event signature for deduplication
        event_signature = self._create_event_signature(event_type, event_data)
        
        # Check if we've already processed this exact event recently
        if event_signature in self._processed_events[event_type]:
            logger.info(f"Skipping duplicate event: {event_type} - {event_signature[:16]}...")
            return
        
        # Add to processed events
        self._processed_events[event_type].add(event_signature)
        
        # Cleanup old events periodically
        self._cleanup_old_events()
        
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
    
    def _create_event_signature(self, event_type, event_data):
        """Create a unique signature for event deduplication"""
        import hashlib
        import json
        
        # Create signature from event type and key data fields
        signature_data = {
            'event_type': event_type,
            'timestamp': event_data.get('timestamp'),
            'basket_id': event_data.get('basket_id'),
            'employee_id': event_data.get('employee_id'),
            'terminal_id': event_data.get('terminal_id')
        }
        
        # Add event-specific fields for better deduplication
        if event_type == 'age.verified':
            signature_data.update({
                'customer_age': event_data.get('customer_age'),
                'verifier_employee_id': event_data.get('verifier_employee_id')
            })
        elif event_type == 'item.added':
            signature_data.update({
                'product_id': event_data.get('product_id'),
                'quantity': event_data.get('quantity')
            })
        
        signature_str = json.dumps(signature_data, sort_keys=True)
        return hashlib.md5(signature_str.encode()).hexdigest()
    
    def _cleanup_old_events(self):
        """Clean up old processed events to prevent memory leaks"""
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            # Clear all processed events older than cleanup interval
            self._processed_events.clear()
            self._last_cleanup = current_time
            logger.info("Cleaned up old processed events")


# Singleton instance
plugin_registry = PluginRegistry()
