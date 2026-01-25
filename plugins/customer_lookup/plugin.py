from plugins.base import BasePlugin
from customers.models import Customer, CustomerLookupLog
from baskets.models import Basket
from .api_client import CustomerAPIClient
from events.producer import event_producer
from django.conf import settings
from django.utils import timezone
from dateutil import parser
import logging
import time

logger = logging.getLogger(__name__)


class CustomerLookupPlugin(BasePlugin):
    name = "customer_lookup"
    description = "Fetches customer data from external system and caches locally"
    
    def get_supported_events(self):
        return ["basket.started"]
    
    def handle_event(self, event_type, event_data):
        """Handle basket started event with customer identifier"""
        if event_type == "basket.started":
            customer_identifier = event_data.get('customer_identifier')
            if customer_identifier:
                self._handle_customer_lookup(event_data)
    
    def _handle_customer_lookup(self, event_data):
        """Process customer lookup and fetch data from external API"""
        try:
            basket_id = event_data.get('basket_id')
            customer_identifier = event_data.get('customer_identifier')
            
            logger.info(f"[CUSTOMER LOOKUP] Processing identifier: {customer_identifier} for basket: {basket_id}")
            
            start_time = time.time()
            
            # Check cache first
            customer = self._check_cache(customer_identifier)
            
            if customer and self._is_cache_fresh(customer):
                logger.info(f"[CUSTOMER LOOKUP] Cache hit for {customer_identifier}")
                self._log_lookup(basket_id, customer_identifier, 'SUCCESS', None, int((time.time() - start_time) * 1000))
            else:
                # Fetch from external API
                logger.info(f"[CUSTOMER LOOKUP] Cache miss, calling external API")
                customer = self._fetch_from_api(basket_id, customer_identifier, start_time)
            
            if customer:
                # Update basket with customer
                self._update_basket(basket_id, customer.customer_id)
                
                # Publish customer data fetched event
                self._publish_customer_data(basket_id, customer)
                
                logger.info(f"[CUSTOMER LOOKUP] Successfully processed {customer.customer_id}")
            else:
                logger.warning(f"[CUSTOMER LOOKUP] Customer not found: {customer_identifier}")
                
        except Exception as e:
            logger.error(f"[CUSTOMER LOOKUP] Error processing customer lookup: {e}")
    
    def _check_cache(self, identifier):
        """Check if customer exists in local cache"""
        try:
            return Customer.objects.get(identifier=identifier)
        except Customer.DoesNotExist:
            return None
    
    def _is_cache_fresh(self, customer):
        """Check if cached customer data is still fresh"""
        cache_ttl = self.config.get('cache_ttl_seconds', 3600)
        age = (timezone.now() - customer.updated_at).total_seconds()
        return age < cache_ttl
    
    def _fetch_from_api(self, basket_id, identifier, start_time):
        """Fetch customer data from external API"""
        api_endpoint = self.config.get('api_endpoint', 'http://localhost:8000/api/mock-customer-lookup/')
        timeout = self.config.get('timeout_seconds', 5)
        retry_attempts = self.config.get('retry_attempts', 2)
        
        api_client = CustomerAPIClient(api_endpoint, timeout, retry_attempts)
        
        try:
            customer_data = api_client.fetch_customer(identifier)
            
            if customer_data:
                # Save or update customer
                customer = self._save_customer(customer_data)
                
                duration_ms = int((time.time() - start_time) * 1000)
                self._log_lookup(basket_id, identifier, 'SUCCESS', customer_data, duration_ms)
                
                return customer
            else:
                duration_ms = int((time.time() - start_time) * 1000)
                self._log_lookup(basket_id, identifier, 'FAILED', None, duration_ms, 'Customer not found')
                return None
                
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_lookup(basket_id, identifier, 'FAILED', None, duration_ms, str(e))
            
            # Fallback to cache on error if configured
            if self.config.get('fallback_to_cache_on_error', True):
                logger.info(f"[CUSTOMER LOOKUP] Falling back to cache")
                return self._check_cache(identifier)
            
            return None
    
    def _save_customer(self, customer_data):
        """Save or update customer in database"""
        customer, created = Customer.objects.update_or_create(
            customer_id=customer_data['customer_id'],
            defaults={
                'identifier': customer_data['identifier'],
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name'],
                'email': customer_data['email'],
                'phone': customer_data['phone'],
                'loyalty_points': customer_data.get('loyalty_points', 0),
                'tier': customer_data.get('tier', 'BRONZE'),
                'total_purchases': customer_data.get('total_purchases', 0),
                'last_purchase_date': parser.parse(customer_data['last_purchase_date']) if customer_data.get('last_purchase_date') else None
            }
        )
        
        action = "Created" if created else "Updated"
        logger.info(f"[CUSTOMER LOOKUP] {action} customer: {customer.customer_id}")
        
        return customer
    
    def _update_basket(self, basket_id, customer_id):
        """Update basket with customer ID"""
        try:
            basket = Basket.objects.get(basket_id=basket_id)
            basket.customer_id = customer_id
            basket.save()
            logger.info(f"[CUSTOMER LOOKUP] Updated basket {basket_id} with customer {customer_id}")
        except Basket.DoesNotExist:
            logger.error(f"[CUSTOMER LOOKUP] Basket not found: {basket_id}")
    
    def _publish_customer_data(self, basket_id, customer):
        """Publish customer data fetched event"""
        event_producer.publish(settings.KAFKA_TOPIC, {
            'event_type': 'CUSTOMER_DATA_FETCHED',
            'timestamp': timezone.now().isoformat(),
            'basket_id': basket_id,
            'customer_id': customer.customer_id,
            'customer_data': {
                'customer_id': customer.customer_id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'phone': customer.phone,
                'loyalty_points': customer.loyalty_points,
                'tier': customer.tier,
                'total_purchases': str(customer.total_purchases)
            }
        })
    
    def _log_lookup(self, basket_id, identifier, status, response_data, duration_ms, error_message=None):
        """Log API lookup for audit trail"""
        api_endpoint = self.config.get('api_endpoint', 'http://localhost:8000/api/mock-customer-lookup/')
        
        CustomerLookupLog.objects.create(
            basket_id=basket_id,
            customer_identifier=identifier,
            api_endpoint=api_endpoint,
            status=status,
            response_data=response_data,
            error_message=error_message,
            duration_ms=duration_ms,
            response_timestamp=timezone.now()
        )
