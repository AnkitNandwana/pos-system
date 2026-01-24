import strawberry
from strawberry import auto
from typing import Optional
import strawberry_django
from .models import Employee


@strawberry_django.type(Employee)
class EmployeeType:
    id: auto
    username: auto
    first_name: auto
    last_name: auto
    email: auto
    role: auto
    employee_id: auto
