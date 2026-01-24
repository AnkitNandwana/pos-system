import strawberry
from strawberry.types import Info
from typing import List
from employees.models import Employee
from employees.types import EmployeeType
from plugins.employee_time_tracker.models import TimeEntry
from plugins.employee_time_tracker.types import TimeEntryType


@strawberry.type
class Query:
    @strawberry.field
    def employees(self) -> List[EmployeeType]:
        return Employee.objects.all()
    
    @strawberry.field
    def my_time_entries(self, info: Info, employee_id: int) -> List[TimeEntryType]:
        return TimeEntry.objects.filter(employee_id=employee_id)
