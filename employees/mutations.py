import strawberry
from strawberry.types import Info
from django.contrib.auth import authenticate
from django.utils import timezone
from employees.models import Employee
from employees.types import EmployeeType
from terminals.models import Terminal
from terminals.types import TerminalType
from terminals.services import TerminalService
from events.producer import event_producer
from events.schemas import EmployeeLoginEvent, EmployeeLogoutEvent, SessionTerminatedEvent
import jwt
from django.conf import settings
from datetime import datetime, timedelta


@strawberry.type
class LoginPayload:
    token: str
    employee: EmployeeType
    terminal: TerminalType


@strawberry.type
class LogoutPayload:
    success: bool
    message: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, username: str, password: str) -> LoginPayload:
        # Authenticate employee
        employee = authenticate(username=username, password=password)
        if not employee:
            raise Exception("Invalid credentials")
        
        # Terminate existing active sessions
        active_terminals = Terminal.objects.filter(employee=employee, is_active=True)
        for old_terminal in active_terminals:
            TerminalService.terminate_active_sessions(employee)
            # Publish session terminated event
            event_data = {
                'event_type': 'SESSION_TERMINATED',
                'employee_id': employee.id,
                'employee_username': employee.username,
                'terminal_id': old_terminal.terminal_id,
                'reason': 'auto_logout',
                'timestamp': timezone.now().isoformat()
            }
            event_producer.publish(settings.KAFKA_TOPIC, event_data)
        
        # Create new terminal session
        terminal = TerminalService.create_session(employee)
        
        # Publish login event
        event_data = {
            'event_type': 'EMPLOYEE_LOGIN',
            'employee_id': employee.id,
            'employee_username': employee.username,
            'terminal_id': terminal.terminal_id,
            'timestamp': timezone.now().isoformat()
        }
        event_producer.publish(settings.KAFKA_TOPIC, event_data)
        
        # Generate JWT token
        token_payload = {
            'user_id': employee.id,
            'username': employee.username,
            'terminal_id': terminal.terminal_id,
            'exp': datetime.utcnow() + timedelta(hours=8)
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')
        
        return LoginPayload(token=token, employee=employee, terminal=terminal)
    
    @strawberry.mutation
    def logout(self, info: Info, terminal_id: str) -> LogoutPayload:
        try:
            terminal = TerminalService.logout_session(terminal_id)
            
            # Publish logout event
            event_data = {
                'event_type': 'EMPLOYEE_LOGOUT',
                'employee_id': terminal.employee.id,
                'employee_username': terminal.employee.username,
                'terminal_id': terminal.terminal_id,
                'timestamp': timezone.now().isoformat()
            }
            event_producer.publish(settings.KAFKA_TOPIC, event_data)
            
            return LogoutPayload(success=True, message="Logged out successfully")
        except Exception as e:
            return LogoutPayload(success=False, message=str(e))
