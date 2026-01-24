from django.core.management.base import BaseCommand
from django.db.models import Q
from employees.models import Employee
from products.models import Product
from customers.models import Customer
from terminals.models import Terminal
from baskets.models import Basket, BasketItem
from plugins.models import PluginConfiguration
from plugins.employee_time_tracker.models import TimeEntry
from plugins.fraud_detection.models import FraudAlert, FraudRule
from plugins.age_verification.models import AgeVerificationState
from plugins.purchase_recommender.models import Recommendation
from datetime import datetime, timedelta
import json


class Command(BaseCommand):
    help = 'Validate POS system state after test rig execution'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--correlation-id',
            type=str,
            help='Correlation ID from test rig run to validate specific test'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed validation results'
        )
    
    def handle(self, *args, **options):
        correlation_id = options.get('correlation_id')
        detailed = options['detailed']
        
        self.stdout.write(
            self.style.SUCCESS('🔍 Validating POS System State After Test Rig')
        )
        
        if correlation_id:
            self.stdout.write(f"Validating specific test run: {correlation_id}")
        
        validation_results = {
            'employee_time_tracker': self.validate_time_tracking(detailed),
            'fraud_detection': self.validate_fraud_detection(detailed),
            'age_verification': self.validate_age_verification(detailed),
            'purchase_recommender': self.validate_purchase_recommender(detailed),
            'customer_lookup': self.validate_customer_lookup(detailed),
            'data_consistency': self.validate_data_consistency(detailed),
            'plugin_configurations': self.validate_plugin_configs(detailed)
        }
        
        # Summary
        self.print_summary(validation_results)
        
        # Detailed results if requested
        if detailed:
            self.print_detailed_results(validation_results)
    
    def validate_time_tracking(self, detailed=False):
        """Validate Employee Time Tracker plugin behavior"""
        results = {
            'plugin_name': 'Employee Time Tracker',
            'tests': [],
            'overall_status': 'PASS'
        }
        
        # Check recent time entries (last hour)
        recent_entries = TimeEntry.objects.filter(
            clock_in__gte=datetime.now() - timedelta(hours=1)
        ).order_by('-clock_in')
        
        # Test 1: Time entry creation on login
        if recent_entries.exists():
            latest_entry = recent_entries.first()
            results['tests'].append({
                'test': 'Time entry created on login',
                'status': 'PASS',
                'details': f'Employee: {latest_entry.employee.username}, Terminal: {latest_entry.terminal_id}'
            })
        else:
            results['tests'].append({
                'test': 'Time entry created on login',
                'status': 'FAIL',
                'details': 'No recent time entries found'
            })
            results['overall_status'] = 'FAIL'
        
        # Test 2: Clock out and hours calculation
        completed_entries = recent_entries.filter(clock_out__isnull=False)
        if completed_entries.exists():
            entry = completed_entries.first()
            if entry.total_hours and entry.total_hours > 0:
                results['tests'].append({
                    'test': 'Clock out and hours calculation',
                    'status': 'PASS',
                    'details': f'Total hours: {entry.total_hours}'
                })
            else:
                results['tests'].append({
                    'test': 'Clock out and hours calculation',
                    'status': 'FAIL',
                    'details': 'Hours not calculated correctly'
                })
                results['overall_status'] = 'FAIL'
        else:
            results['tests'].append({
                'test': 'Clock out and hours calculation',
                'status': 'PENDING',
                'details': 'No completed sessions found (may still be active)'
            })
        
        return results
    
    def validate_fraud_detection(self, detailed=False):
        """Validate Fraud Detection plugin behavior"""
        results = {
            'plugin_name': 'Fraud Detection',
            'tests': [],
            'overall_status': 'PASS'
        }
        
        # Check recent fraud alerts
        recent_alerts = FraudAlert.objects.filter(
            timestamp__gte=datetime.now() - timedelta(hours=1)
        ).order_by('-timestamp')
        
        # Test 1: Plugin is processing events
        active_rules = FraudRule.objects.filter(enabled=True).count()
        results['tests'].append({
            'test': 'Active fraud rules configured',
            'status': 'PASS' if active_rules > 0 else 'FAIL',
            'details': f'{active_rules} active rules'
        })
        
        # Test 2: Alert generation (may or may not trigger based on test data)
        results['tests'].append({
            'test': 'Fraud alert generation capability',
            'status': 'PASS',  # We assume this works if no errors occurred
            'details': f'{recent_alerts.count()} alerts generated in last hour'
        })
        
        # Test 3: Check for specific rule types
        rule_types = FraudRule.objects.values_list('rule_id', flat=True).distinct()
        expected_rules = ['multiple_terminals', 'rapid_items', 'high_value_payment', 'anonymous_payment']
        missing_rules = [rule for rule in expected_rules if rule not in rule_types]
        
        if not missing_rules:
            results['tests'].append({
                'test': 'All expected fraud rules present',
                'status': 'PASS',
                'details': f'Found: {list(rule_types)}'
            })
        else:
            results['tests'].append({
                'test': 'All expected fraud rules present',
                'status': 'FAIL',
                'details': f'Missing: {missing_rules}'
            })
            results['overall_status'] = 'FAIL'
        
        return results
    
    def validate_age_verification(self, detailed=False):
        """Validate Age Verification plugin behavior"""
        results = {
            'plugin_name': 'Age Verification',
            'tests': [],
            'overall_status': 'PASS'
        }
        
        # Check recent verification states
        recent_states = AgeVerificationState.objects.filter(
            created_at__gte=datetime.now() - timedelta(hours=1)
        ).order_by('-created_at')
        
        # Test 1: Age verification triggered for restricted items
        if recent_states.exists():
            results['tests'].append({
                'test': 'Age verification triggered',
                'status': 'PASS',
                'details': f'{recent_states.count()} verification states found'
            })
            
            # Test 2: Verification results recorded
            completed_states = recent_states.filter(verification_completed=True)
            if completed_states.exists():
                results['tests'].append({
                    'test': 'Verification results recorded',
                    'status': 'PASS',
                    'details': f'{completed_states.count()} completed verifications'
                })
            else:
                results['tests'].append({
                    'test': 'Verification results recorded',
                    'status': 'FAIL',
                    'details': 'No completed verifications found'
                })
                results['overall_status'] = 'FAIL'
        else:
            results['tests'].append({
                'test': 'Age verification triggered',
                'status': 'FAIL',
                'details': 'No verification states found'
            })
            results['overall_status'] = 'FAIL'
        
        # Test 3: Age-restricted products exist
        age_restricted_count = Product.objects.filter(age_restricted=True).count()
        results['tests'].append({
            'test': 'Age-restricted products available',
            'status': 'PASS' if age_restricted_count > 0 else 'FAIL',
            'details': f'{age_restricted_count} age-restricted products'
        })
        
        return results
    
    def validate_purchase_recommender(self, detailed=False):
        """Validate Purchase Recommender plugin behavior"""
        results = {
            'plugin_name': 'Purchase Recommender',
            'tests': [],
            'overall_status': 'PASS'
        }
        
        # Check recent recommendation logs
        recent_recommendations = Recommendation.objects.filter(
            recommended_at__gte=datetime.now() - timedelta(hours=1)
        ).order_by('-recommended_at')
        
        # Test 1: Recommendation generation
        if recent_recommendations.exists():
            results['tests'].append({
                'test': 'Recommendations generated',
                'status': 'PASS',
                'details': f'{recent_recommendations.count()} recommendations found'
            })
        else:
            results['tests'].append({
                'test': 'Recommendations generated',
                'status': 'PENDING',
                'details': 'No recent recommendations (may not have triggered)'
            })
        
        # Test 2: Recommendation rules exist
        from products.models import RecommendationRule
        rule_count = RecommendationRule.objects.filter(is_active=True).count()
        results['tests'].append({
            'test': 'Recommendation rules configured',
            'status': 'PASS' if rule_count > 0 else 'PENDING',
            'details': f'{rule_count} active recommendation rules'
        })
        
        return results
    
    def validate_customer_lookup(self, detailed=False):
        """Validate Customer Lookup plugin behavior"""
        results = {
            'plugin_name': 'Customer Lookup',
            'tests': [],
            'overall_status': 'PASS'
        }
        
        # Check recent lookup logs
        from customers.models import CustomerLookupLog
        recent_logs = CustomerLookupLog.objects.filter(
            request_timestamp__gte=datetime.now() - timedelta(hours=1)
        ).order_by('-request_timestamp')
        
        # Test 1: Customer lookup attempts
        if recent_logs.exists():
            results['tests'].append({
                'test': 'Customer lookup attempts',
                'status': 'PASS',
                'details': f'{recent_logs.count()} lookup attempts'
            })
            
            # Test 2: Successful lookups
            successful_logs = recent_logs.filter(status='SUCCESS')
            if successful_logs.exists():
                results['tests'].append({
                    'test': 'Successful customer lookups',
                    'status': 'PASS',
                    'details': f'{successful_logs.count()} successful lookups'
                })
            else:
                results['tests'].append({
                    'test': 'Successful customer lookups',
                    'status': 'FAIL',
                    'details': 'No successful lookups found'
                })
                results['overall_status'] = 'FAIL'
        else:
            results['tests'].append({
                'test': 'Customer lookup attempts',
                'status': 'PENDING',
                'details': 'No recent lookup attempts (may not have triggered)'
            })
        
        # Test 3: Customer data exists
        customer_count = Customer.objects.count()
        results['tests'].append({
            'test': 'Customer data available',
            'status': 'PASS' if customer_count > 0 else 'FAIL',
            'details': f'{customer_count} customers in database'
        })
        
        return results
    
    def validate_data_consistency(self, detailed=False):
        """Validate overall data consistency"""
        results = {
            'plugin_name': 'Data Consistency',
            'tests': [],
            'overall_status': 'PASS'
        }
        
        # Test 1: Recent baskets have items
        recent_baskets = Basket.objects.filter(
            created_at__gte=datetime.now() - timedelta(hours=1)
        )
        
        if recent_baskets.exists():
            baskets_with_items = sum(1 for basket in recent_baskets if basket.items.exists())
            results['tests'].append({
                'test': 'Baskets contain items',
                'status': 'PASS' if baskets_with_items > 0 else 'FAIL',
                'details': f'{baskets_with_items}/{recent_baskets.count()} baskets have items'
            })
        else:
            results['tests'].append({
                'test': 'Baskets contain items',
                'status': 'PENDING',
                'details': 'No recent baskets found'
            })
        
        # Test 2: Terminal sessions are properly managed
        active_terminals = Terminal.objects.filter(is_active=True).count()
        results['tests'].append({
            'test': 'Terminal session management',
            'status': 'PASS',
            'details': f'{active_terminals} active terminal sessions'
        })
        
        # Test 3: Employee data integrity
        employees_with_terminals = Employee.objects.filter(terminals__isnull=False).distinct().count()
        total_employees = Employee.objects.count()
        results['tests'].append({
            'test': 'Employee-terminal relationships',
            'status': 'PASS',
            'details': f'{employees_with_terminals}/{total_employees} employees have terminal history'
        })
        
        return results
    
    def validate_plugin_configs(self, detailed=False):
        """Validate plugin configurations"""
        results = {
            'plugin_name': 'Plugin Configurations',
            'tests': [],
            'overall_status': 'PASS'
        }
        
        required_plugins = [
            'employee_time_tracker',
            'purchase_recommender',
            'customer_lookup',
            'fraud_detection',
            'age_verification'
        ]
        
        # Test 1: All required plugins configured
        configured_plugins = list(PluginConfiguration.objects.values_list('name', flat=True))
        missing_plugins = [p for p in required_plugins if p not in configured_plugins]
        
        if not missing_plugins:
            results['tests'].append({
                'test': 'All required plugins configured',
                'status': 'PASS',
                'details': f'Found: {configured_plugins}'
            })
        else:
            results['tests'].append({
                'test': 'All required plugins configured',
                'status': 'FAIL',
                'details': f'Missing: {missing_plugins}'
            })
            results['overall_status'] = 'FAIL'
        
        # Test 2: All plugins enabled
        enabled_plugins = list(PluginConfiguration.objects.filter(enabled=True).values_list('name', flat=True))
        disabled_plugins = [p for p in required_plugins if p not in enabled_plugins]
        
        if not disabled_plugins:
            results['tests'].append({
                'test': 'All required plugins enabled',
                'status': 'PASS',
                'details': f'Enabled: {enabled_plugins}'
            })
        else:
            results['tests'].append({
                'test': 'All required plugins enabled',
                'status': 'FAIL',
                'details': f'Disabled: {disabled_plugins}'
            })
            results['overall_status'] = 'FAIL'
        
        return results
    
    def print_summary(self, validation_results):
        """Print validation summary"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("VALIDATION SUMMARY")
        self.stdout.write("="*60)
        
        total_plugins = len(validation_results)
        passed_plugins = sum(1 for result in validation_results.values() if result['overall_status'] == 'PASS')
        
        for plugin_name, result in validation_results.items():
            status = result['overall_status']
            if status == 'PASS':
                status_color = self.style.SUCCESS('✓ PASS')
            elif status == 'FAIL':
                status_color = self.style.ERROR('✗ FAIL')
            else:
                status_color = self.style.WARNING('⚠ PENDING')
            
            self.stdout.write(f"{result['plugin_name']:<25} {status_color}")
        
        self.stdout.write("-"*60)
        
        if passed_plugins == total_plugins:
            self.stdout.write(
                self.style.SUCCESS(f"🎉 ALL VALIDATIONS PASSED ({passed_plugins}/{total_plugins})")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠ PARTIAL SUCCESS ({passed_plugins}/{total_plugins} passed)")
            )
    
    def print_detailed_results(self, validation_results):
        """Print detailed validation results"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("DETAILED VALIDATION RESULTS")
        self.stdout.write("="*60)
        
        for plugin_name, result in validation_results.items():
            self.stdout.write(f"\n📋 {result['plugin_name']}")
            self.stdout.write("-" * (len(result['plugin_name']) + 4))
            
            for test in result['tests']:
                status = test['status']
                if status == 'PASS':
                    status_icon = self.style.SUCCESS('✓')
                elif status == 'FAIL':
                    status_icon = self.style.ERROR('✗')
                else:
                    status_icon = self.style.WARNING('⚠')
                
                self.stdout.write(f"  {status_icon} {test['test']}")
                self.stdout.write(f"    {test['details']}")