from plugins.base import BasePlugin
from .models import TimeEntry
from employees.models import Employee
from dateutil import parser
import logging

logger = logging.getLogger(__name__)


class EmployeeTimeTrackerPlugin(BasePlugin):
    name = "employee_time_tracker"
    description = "Tracks employee login/logout times and calculates work hours"
    
    def get_supported_events(self):
        return ["EMPLOYEE_LOGIN", "EMPLOYEE_LOGOUT", "SESSION_TERMINATED"]
    
    def handle_event(self, event_type, event_data):
        """Handle employee time tracking events"""
        if event_type == "EMPLOYEE_LOGIN":
            self._handle_login(event_data)
        elif event_type in ["EMPLOYEE_LOGOUT", "SESSION_TERMINATED"]:
            self._handle_logout(event_data)
    
    def _handle_login(self, event_data):
        """Create time entry on employee login"""
        try:
            employee = Employee.objects.get(id=event_data['employee_id'])
            TimeEntry.objects.create(
                employee=employee,
                terminal_id=event_data['terminal_id'],
                clock_in=parser.parse(event_data['timestamp'])
            )
            logger.info(f"[TIME ENTRY] Clock In - Employee: {employee.username}, Terminal: {event_data['terminal_id']}")
        except Exception as e:
            logger.error(f"Failed to create time entry: {e}")
    
    def _handle_logout(self, event_data):
        """Update time entry on employee logout"""
        try:
            employee = Employee.objects.get(id=event_data['employee_id'])
            time_entry = TimeEntry.objects.filter(
                employee=employee,
                terminal_id=event_data['terminal_id'],
                clock_out__isnull=True
            ).first()
            
            if time_entry:
                time_entry.clock_out = parser.parse(event_data['timestamp'])
                time_entry.calculate_hours()
                logger.info(f"[TIME ENTRY] Clock Out - Employee: {employee.username}, Hours: {time_entry.total_hours}")
        except Exception as e:
            logger.error(f"Failed to update time entry: {e}")
