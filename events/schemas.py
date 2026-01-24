from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EmployeeLoginEvent:
    event_type: str = "EMPLOYEE_LOGIN"
    employee_id: int = None
    employee_username: str = None
    terminal_id: str = None
    timestamp: str = None


@dataclass
class EmployeeLogoutEvent:
    event_type: str = "EMPLOYEE_LOGOUT"
    employee_id: int = None
    employee_username: str = None
    terminal_id: str = None
    timestamp: str = None


@dataclass
class SessionTerminatedEvent:
    event_type: str = "SESSION_TERMINATED"
    employee_id: int = None
    employee_username: str = None
    terminal_id: str = None
    reason: str = "auto_logout"
    timestamp: str = None
