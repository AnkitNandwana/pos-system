from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """Base class for all plugins"""
    
    name = None
    description = None
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def can_handle(self, event_type):
        """Check if plugin can handle this event type"""
        return event_type in self.get_supported_events()
    
    @abstractmethod
    def get_supported_events(self):
        """Return list of event types this plugin supports"""
        pass
    
    @abstractmethod
    def handle_event(self, event_type, event_data):
        """Handle the event"""
        pass
