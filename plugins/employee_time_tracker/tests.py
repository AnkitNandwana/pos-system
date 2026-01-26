from datetime import datetime, timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from employees.models import Employee
from plugins.models import PluginConfiguration
from plugins.registry import PluginRegistry
from plugins.employee_time_tracker.plugin import EmployeeTimeTrackerPlugin
from plugins.employee_time_tracker.models import TimeEntry


class EmployeeTimeTrackerPluginTest(TestCase):
    """Test Employee Time Tracker plugin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.plugin_config = PluginConfiguration.objects.create(
            name='employee_time_tracker',
            enabled=True,
            description='Test configuration'
        )
        
        self.employee = Employee.objects.create_user(
            username='john_doe',
            password='testpass123',
            employee_id='EMP001',
            role='CASHIER'
        )
        
        self.plugin = EmployeeTimeTrackerPlugin()
        
        self.registry = PluginRegistry()
        self.registry.register(EmployeeTimeTrackerPlugin)
    
    def test_plugin_processes_events_when_enabled(self):
        """Plugin should process events when enabled"""
        base_time = timezone.now()
        event_data = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'timestamp': base_time.isoformat()
        }
        
        with freeze_time(base_time):
            self.registry.route_event('EMPLOYEE_LOGIN', event_data)
        
        self.assertTrue(TimeEntry.objects.filter(employee=self.employee).exists())
    
    def test_plugin_ignores_events_when_disabled(self):
        """Plugin should not process events when disabled"""
        self.plugin_config.enabled = False
        self.plugin_config.save()
        
        event_data = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'timestamp': timezone.now().isoformat()
        }
        
        self.registry.route_event('EMPLOYEE_LOGIN', event_data)
        self.assertFalse(TimeEntry.objects.filter(employee=self.employee).exists())
    
    def test_login_creates_time_entry(self):
        """Login should create a new time entry"""
        base_time = timezone.now()
        event_data = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'timestamp': base_time.isoformat()
        }
        
        with freeze_time(base_time):
            self.plugin.handle_event('EMPLOYEE_LOGIN', event_data)
        
        time_entry = TimeEntry.objects.get(employee=self.employee)
        self.assertEqual(time_entry.terminal_id, 'TERM-001')
        self.assertEqual(time_entry.clock_in, base_time)
        self.assertIsNone(time_entry.clock_out)
    
    def test_logout_completes_time_entry(self):
        """Logout should complete time entry and calculate hours"""
        login_time = timezone.now()
        logout_time = login_time + timedelta(hours=8)
        
        # Create active time entry
        time_entry = TimeEntry.objects.create(
            employee=self.employee,
            terminal_id='TERM-001',
            clock_in=login_time
        )
        
        event_data = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'timestamp': logout_time.isoformat()
        }
        
        with freeze_time(logout_time):
            self.plugin.handle_event('EMPLOYEE_LOGOUT', event_data)
        
        time_entry.refresh_from_db()
        self.assertEqual(time_entry.clock_out, logout_time)
        self.assertEqual(time_entry.total_hours, Decimal('8.00'))
    
    def test_accurate_time_calculation(self):
        """Time calculation should be accurate"""
        login_time = timezone.now()
        logout_time = login_time + timedelta(hours=7, minutes=30)  # 7.5 hours
        
        time_entry = TimeEntry.objects.create(
            employee=self.employee,
            terminal_id='TERM-001',
            clock_in=login_time
        )
        
        event_data = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'timestamp': logout_time.isoformat()
        }
        
        with freeze_time(logout_time):
            self.plugin.handle_event('EMPLOYEE_LOGOUT', event_data)
        
        time_entry.refresh_from_db()
        self.assertEqual(time_entry.total_hours, Decimal('7.50'))
    
    def test_complete_session_workflow(self):
        """Test complete login to logout workflow"""
        login_time = timezone.now()
        logout_time = login_time + timedelta(hours=8)
        
        # Employee logs in
        login_event = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'timestamp': login_time.isoformat()
        }
        
        with freeze_time(login_time):
            self.registry.route_event('EMPLOYEE_LOGIN', login_event)
        
        # Verify session created
        time_entry = TimeEntry.objects.get(employee=self.employee)
        self.assertEqual(time_entry.clock_in, login_time)
        self.assertIsNone(time_entry.clock_out)
        
        # Employee logs out
        logout_event = {
            'employee_id': self.employee.id,
            'terminal_id': 'TERM-001',
            'timestamp': logout_time.isoformat()
        }
        
        with freeze_time(logout_time):
            self.registry.route_event('EMPLOYEE_LOGOUT', logout_event)
        
        # Verify session completed
        time_entry.refresh_from_db()
        self.assertEqual(time_entry.clock_out, logout_time)
        self.assertEqual(time_entry.total_hours, Decimal('8.00'))