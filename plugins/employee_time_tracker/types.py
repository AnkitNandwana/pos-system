import strawberry
from strawberry import auto
from typing import Optional
from datetime import datetime
from decimal import Decimal
import strawberry_django
from .models import TimeEntry
from employees.types import EmployeeType


@strawberry_django.type(TimeEntry)
class TimeEntryType:
    id: auto
    employee: EmployeeType
    terminal_id: auto
    clock_in: auto
    clock_out: Optional[datetime]
    total_hours: Optional[Decimal]
