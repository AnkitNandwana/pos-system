from django.core.management.base import BaseCommand
from employees.models import Employee


class Command(BaseCommand):
    help = 'Seed sample employees for testing'
    
    def handle(self, *args, **options):
        employees = [
            {
                'username': 'john',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'employee_id': 'EMP001',
                'role': 'CASHIER'
            },
            {
                'username': 'jane',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane@example.com',
                'employee_id': 'EMP002',
                'role': 'MANAGER'
            },
            {
                'username': 'admin',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@example.com',
                'employee_id': 'EMP003',
                'role': 'ADMIN'
            }
        ]
        
        created_count = 0
        for emp_data in employees:
            password = emp_data.pop('password')
            employee, created = Employee.objects.get_or_create(
                username=emp_data['username'],
                defaults=emp_data
            )
            
            if created:
                employee.set_password(password)
                employee.save()
                created_count += 1
                self.stdout.write(f"Created: {employee.username} ({employee.role})")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Seeded {created_count} employees!'))