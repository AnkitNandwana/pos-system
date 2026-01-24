import strawberry
from strawberry import auto
from typing import Optional
from datetime import datetime
import strawberry_django
from .models import Terminal
from employees.types import EmployeeType


@strawberry_django.type(Terminal)
class TerminalType:
    id: auto
    terminal_id: auto
    employee: EmployeeType
    login_time: auto
    logout_time: Optional[datetime]
    is_active: auto
