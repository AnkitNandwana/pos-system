from django.db import transaction
from django.utils import timezone
from .models import Terminal
import uuid


class TerminalService:
    @staticmethod
    def terminate_active_sessions(employee):
        """Terminate all active sessions for an employee"""
        with transaction.atomic():
            Terminal.objects.select_for_update().filter(
                employee=employee,
                is_active=True
            ).update(
                is_active=False,
                logout_time=timezone.now()
            )
    
    @staticmethod
    def create_session(employee):
        """Create a new terminal session"""
        terminal = Terminal.objects.create(
            terminal_id=str(uuid.uuid4()),
            employee=employee,
            is_active=True
        )
        return terminal
    
    @staticmethod
    def logout_session(terminal_id):
        """Logout a specific terminal session"""
        with transaction.atomic():
            terminal = Terminal.objects.select_for_update().get(
                terminal_id=terminal_id,
                is_active=True
            )
            terminal.is_active = False
            terminal.logout_time = timezone.now()
            terminal.save()
            return terminal
