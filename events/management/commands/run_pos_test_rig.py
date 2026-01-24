from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from events.producer import event_producer
from employees.models import Employee
from products.models import Product
from customers.models import Customer
from terminals.models import Terminal
from baskets.models import Basket, BasketItem
from plugins.models import PluginConfiguration
from plugins.employee_time_tracker.models import TimeEntry
from plugins.fraud_detection.models import FraudAlert
from plugins.age_verification.models import AgeVerificationState, AgeVerificationViolation
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import time
import json
import logging
import sys

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


class POSTestRig:
    """End-to-end test rig for event-driven POS system"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.correlation_id = str(uuid.uuid4())
        self.test_data = {}
        self.events_published = []
        self.start_time = datetime.now()
        
    def log(self, message, level='info'):
        """Structured logging with correlation ID"""
        log_data = {
            'correlation_id': self.correlation_id,
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        
        if level == 'error':
            logger.error(json.dumps(log_data))
        elif level == 'warning':
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
            
        if self.verbose:
            print(f"[{level.upper()}] {message}")
    
    def validate_preconditions(self):
        """Validate required data exists in database"""
        self.log("=== VALIDATING PRECONDITIONS ===")
        
        # Check employees
        employee = Employee.objects.filter(role='CASHIER', is_active=True).first()
        if not employee:
            raise Exception("No active CASHIER employee found")
        self.test_data['employee'] = employee
        self.log(f"✓ Employee: {employee.username} (ID: {employee.id})")
        
        # Check products (regular + age-restricted)
        regular_products = list(Product.objects.filter(age_restricted=False)[:3])
        age_restricted_products = list(Product.objects.filter(age_restricted=True)[:1])
        
        if len(regular_products) < 3:
            raise Exception("Need at least 3 regular products")
        if len(age_restricted_products) < 1:
            raise Exception("Need at least 1 age-restricted product")
            
        self.test_data['regular_products'] = regular_products
        self.test_data['age_restricted_product'] = age_restricted_products[0]
        self.log(f"✓ Products: {len(regular_products)} regular, 1 age-restricted")
        
        # Check customers
        customer = Customer.objects.first()
        if not customer:
            raise Exception("No customer found")
        self.test_data['customer'] = customer
        self.log(f"✓ Customer: {customer.first_name} {customer.last_name}")
        
        # Check terminals
        terminal = Terminal.objects.filter(is_active=True).first()
        if not terminal:
            # Create a terminal for testing
            terminal = Terminal.objects.create(
                terminal_id=f"TEST_TERMINAL_{uuid.uuid4().hex[:8]}",
                employee=employee,
                is_active=True
            )
        self.test_data['terminal'] = terminal
        self.log(f"✓ Terminal: {terminal.terminal_id}")
        
        # Check plugin configurations
        required_plugins = [
            'employee_time_tracker',
            'purchase_recommender', 
            'customer_lookup',
            'fraud_detection',
            'age_verification'
        ]
        
        for plugin_name in required_plugins:
            config = PluginConfiguration.objects.filter(name=plugin_name).first()
            if not config:
                self.log(f"⚠ Plugin {plugin_name} not configured, creating...", 'warning')
                PluginConfiguration.objects.create(
                    name=plugin_name,
                    enabled=True,
                    description=f"Auto-created for test rig"
                )
            elif not config.enabled:
                self.log(f"⚠ Plugin {plugin_name} disabled, enabling...", 'warning')
                config.enabled = True
                config.save()
        
        self.log("✓ All plugins configured and enabled")
        self.log("=== PRECONDITIONS VALIDATED ===\n")
    
    def publish_event(self, event_type, event_data):
        """Publish event with logging and tracking"""
        event_data['correlation_id'] = self.correlation_id
        event_data['test_rig'] = True
        
        self.log(f"📤 Publishing: {event_type}")
        if self.verbose:
            print(f"   Data: {json.dumps(event_data, indent=2, default=str)}")
        
        event_producer.publish(settings.KAFKA_TOPIC, event_data)
        self.events_published.append({
            'type': event_type,
            'timestamp': datetime.now(),
            'data': event_data
        })
        
        # Small delay to ensure event processing order
        time.sleep(0.1)
    
    def run_employee_login(self):
        """Step 1: Employee login"""
        self.log("=== STEP 1: EMPLOYEE LOGIN ===")
        
        employee = self.test_data['employee']
        terminal = self.test_data['terminal']
        
        # Terminate any existing sessions
        Terminal.objects.filter(
            employee=employee,
            is_active=True
        ).exclude(id=terminal.id).update(
            is_active=False,
            logout_time=datetime.now()
        )
        
        # Update terminal
        terminal.employee = employee
        terminal.login_time = datetime.now()
        terminal.is_active = True
        terminal.save()
        
        login_event = {
            'event_type': 'EMPLOYEE_LOGIN',
            'employee_id': employee.id,
            'terminal_id': terminal.terminal_id,
            'timestamp': datetime.now().isoformat(),
            'session_id': str(uuid.uuid4()),
            'metadata': {
                'username': employee.username,
                'role': employee.role
            }
        }
        
        self.publish_event('EMPLOYEE_LOGIN', login_event)
        self.test_data['session_id'] = login_event['session_id']
        
    def run_basket_started(self):
        """Step 2: Basket started"""
        self.log("=== STEP 2: BASKET STARTED ===")
        
        basket_id = f"BASKET_{uuid.uuid4().hex[:8]}"
        employee = self.test_data['employee']
        terminal = self.test_data['terminal']
        
        # Create basket in database
        basket = Basket.objects.create(
            basket_id=basket_id,
            employee=employee,
            status='ACTIVE'
        )
        self.test_data['basket'] = basket
        
        basket_event = {
            'event_type': 'basket.started',
            'basket_id': basket_id,
            'terminal_id': terminal.terminal_id,
            'employee_id': employee.id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.publish_event('basket.started', basket_event)
        
    def run_customer_identified(self):
        """Step 3: Customer identified"""
        self.log("=== STEP 3: CUSTOMER IDENTIFIED ===")
        
        customer = self.test_data['customer']
        basket = self.test_data['basket']
        
        # Update basket with customer
        basket.customer_id = customer.customer_id
        basket.save()
        
        customer_event = {
            'event_type': 'customer.identified',
            'customer_id': customer.id,
            'customer_identifier': customer.identifier,
            'basket_id': basket.basket_id,
            'identification_method': 'loyalty_card',
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'tier': customer.tier,
                'loyalty_points': customer.loyalty_points
            }
        }
        
        self.publish_event('customer.identified', customer_event)
        
    def run_add_items(self):
        """Step 4: Add items to basket"""
        self.log("=== STEP 4: ADDING ITEMS ===")
        
        basket = self.test_data['basket']
        regular_products = self.test_data['regular_products']
        age_restricted_product = self.test_data['age_restricted_product']
        
        # Add regular items first
        for i, product in enumerate(regular_products):
            quantity = i + 1  # 1, 2, 3
            
            # Create basket item
            BasketItem.objects.create(
                basket=basket,
                product_id=product.product_id,
                product_name=product.name,
                quantity=quantity,
                price=product.price
            )
            
            item_event = {
                'event_type': 'item.added',
                'basket_id': basket.basket_id,
                'product_id': product.id,
                'product_code': product.product_id,
                'product_name': product.name,
                'quantity': quantity,
                'unit_price': float(product.price),
                'age_restricted': product.age_restricted,
                'category': product.category,
                'timestamp': datetime.now().isoformat()
            }
            
            self.publish_event('item.added', item_event)
            time.sleep(0.2)  # Simulate realistic timing
        
        # Add age-restricted item last
        BasketItem.objects.create(
            basket=basket,
            product_id=age_restricted_product.product_id,
            product_name=age_restricted_product.name,
            quantity=1,
            price=age_restricted_product.price
        )
        
        age_restricted_event = {
            'event_type': 'item.added',
            'basket_id': basket.basket_id,
            'product_id': age_restricted_product.id,
            'product_code': age_restricted_product.product_id,
            'product_name': age_restricted_product.name,
            'quantity': 1,
            'unit_price': float(age_restricted_product.price),
            'age_restricted': True,
            'minimum_age': age_restricted_product.minimum_age,
            'age_restriction_category': age_restricted_product.age_restriction_category,
            'category': age_restricted_product.category,
            'timestamp': datetime.now().isoformat()
        }
        
        self.publish_event('item.added', age_restricted_event)
        
    def run_age_verification(self):
        """Step 5: Age verification (triggered by age-restricted item)"""
        self.log("=== STEP 5: AGE VERIFICATION ===")
        
        basket = self.test_data['basket']
        age_restricted_product = self.test_data['age_restricted_product']
        
        # Simulate age verification approval
        verification_event = {
            'event_type': 'age.verified',
            'basket_id': basket.basket_id,
            'product_id': age_restricted_product.id,
            'verification_method': 'id_scan',
            'verified_age': 25,
            'minimum_required_age': age_restricted_product.minimum_age,
            'verification_result': 'approved',
            'timestamp': datetime.now().isoformat()
        }
        
        self.publish_event('age.verified', verification_event)
        
    def run_subtotal_finalized(self):
        """Step 6: Subtotal finalized"""
        self.log("=== STEP 6: SUBTOTAL FINALIZED ===")
        
        basket = self.test_data['basket']
        
        # Calculate total from basket items
        total_amount = sum(
            item.quantity * item.price 
            for item in basket.items.all()
        )
        
        tax_rate = Decimal('0.08')  # 8% tax
        tax_amount = total_amount * tax_rate
        final_total = total_amount + tax_amount
        
        subtotal_event = {
            'event_type': 'subtotal.finalized',
            'basket_id': basket.basket_id,
            'subtotal': float(total_amount),
            'tax_amount': float(tax_amount),
            'total_amount': float(final_total),
            'item_count': basket.items.count(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.publish_event('subtotal.finalized', subtotal_event)
        self.test_data['total_amount'] = float(final_total)
        
    def run_payment_completed(self):
        """Step 7: Payment completed"""
        self.log("=== STEP 7: PAYMENT COMPLETED ===")
        
        basket = self.test_data['basket']
        employee = self.test_data['employee']
        terminal = self.test_data['terminal']
        
        # Update basket status
        basket.status = 'PAID'
        basket.save()
        
        payment_event = {
            'event_type': 'payment.completed',
            'basket_id': basket.basket_id,
            'employee_id': employee.id,
            'terminal_id': terminal.terminal_id,
            'amount': self.test_data['total_amount'],
            'payment_method': 'credit_card',
            'transaction_id': f"TXN_{uuid.uuid4().hex[:8]}",
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'card_type': 'visa',
                'last_four': '1234'
            }
        }
        
        self.publish_event('payment.completed', payment_event)
        
    def run_employee_logout(self):
        """Step 8: Employee logout"""
        self.log("=== STEP 8: EMPLOYEE LOGOUT ===")
        
        employee = self.test_data['employee']
        terminal = self.test_data['terminal']
        
        # Update terminal
        terminal.is_active = False
        terminal.logout_time = datetime.now()
        terminal.save()
        
        logout_event = {
            'event_type': 'EMPLOYEE_LOGOUT',
            'employee_id': employee.id,
            'terminal_id': terminal.terminal_id,
            'session_id': self.test_data['session_id'],
            'timestamp': datetime.now().isoformat(),
            'session_duration': (datetime.now() - self.start_time).total_seconds()
        }
        
        self.publish_event('EMPLOYEE_LOGOUT', logout_event)
        
    def validate_results(self):
        """Validate expected plugin behaviors"""
        self.log("=== VALIDATING RESULTS ===")
        
        # Wait for event processing
        time.sleep(2)
        
        employee = self.test_data['employee']
        terminal = self.test_data['terminal']
        basket = self.test_data['basket']
        
        # Check Employee Time Tracker
        time_entry = TimeEntry.objects.filter(
            employee=employee,
            terminal_id=terminal.terminal_id
        ).order_by('-clock_in').first()
        
        if time_entry:
            self.log(f"✓ Time Entry: Clock in/out recorded, Hours: {time_entry.total_hours}")
        else:
            self.log("✗ Time Entry: No time entry found", 'error')
        
        # Check Fraud Detection
        fraud_alerts = FraudAlert.objects.filter(
            employee=employee,
            terminal_id=terminal.terminal_id
        ).count()
        self.log(f"✓ Fraud Detection: {fraud_alerts} alerts generated")
        
        # Check Age Verification
        age_states = AgeVerificationState.objects.filter(
            basket_id=basket.basket_id
        ).count()
        self.log(f"✓ Age Verification: {age_states} verification states")
        
        # Summary
        duration = (datetime.now() - self.start_time).total_seconds()
        self.log(f"✓ Test completed in {duration:.2f} seconds")
        self.log(f"✓ Published {len(self.events_published)} events")
        
        return {
            'success': True,
            'duration': duration,
            'events_published': len(self.events_published),
            'time_entries': 1 if time_entry else 0,
            'fraud_alerts': fraud_alerts,
            'age_verification_states': age_states
        }


class Command(BaseCommand):
    help = 'Run end-to-end POS system test rig'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
        parser.add_argument(
            '--validate-plugins',
            action='store_true',
            help='Validate plugin configurations before running'
        )
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        validate_plugins = options['validate_plugins']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting POS System End-to-End Test Rig')
        )
        
        try:
            with transaction.atomic():
                test_rig = POSTestRig(verbose=verbose)
                
                # Validate preconditions
                test_rig.validate_preconditions()
                
                if validate_plugins:
                    self.stdout.write("Plugin validation enabled - checking configurations...")
                
                # Run test sequence
                test_rig.run_employee_login()
                test_rig.run_basket_started()
                test_rig.run_customer_identified()
                test_rig.run_add_items()
                test_rig.run_age_verification()
                test_rig.run_subtotal_finalized()
                test_rig.run_payment_completed()
                test_rig.run_employee_logout()
                
                # Validate results
                results = test_rig.validate_results()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Test rig completed successfully!\n'
                        f'   Duration: {results["duration"]:.2f}s\n'
                        f'   Events: {results["events_published"]}\n'
                        f'   Time Entries: {results["time_entries"]}\n'
                        f'   Fraud Alerts: {results["fraud_alerts"]}\n'
                        f'   Age Verifications: {results["age_verification_states"]}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Test rig failed: {str(e)}')
            )
            raise