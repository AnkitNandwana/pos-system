from plugins.base import BasePlugin
from .models import Recommendation
from products.models import RecommendationRule
from events.producer import event_producer
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class PurchaseRecommenderPlugin(BasePlugin):
    name = "purchase_recommender"
    description = "Recommends additional items based on basket contents"
    
    # Hardcoded recommendation rules (fallback)
    HARDCODED_RULES = {
        'BURGER': [
            {'product_id': 'FRIES', 'name': 'French Fries', 'price': '2.99'},
            {'product_id': 'COKE', 'name': 'Coca Cola', 'price': '1.99'}
        ],
        'COFFEE': [
            {'product_id': 'DONUT', 'name': 'Donut', 'price': '1.99'},
            {'product_id': 'MUFFIN', 'name': 'Blueberry Muffin', 'price': '2.49'}
        ],
        'LAPTOP': [
            {'product_id': 'MOUSE', 'name': 'Wireless Mouse', 'price': '29.99'},
            {'product_id': 'LAPTOP_BAG', 'name': 'Laptop Bag', 'price': '39.99'}
        ],
        'PHONE': [
            {'product_id': 'PHONE_CASE', 'name': 'Phone Case', 'price': '19.99'},
            {'product_id': 'SCREEN_PROTECTOR', 'name': 'Screen Protector', 'price': '9.99'}
        ],
        'PIZZA': [
            {'product_id': 'GARLIC_BREAD', 'name': 'Garlic Bread', 'price': '4.99'},
            {'product_id': 'SODA', 'name': 'Soda', 'price': '2.49'}
        ],
    }
    
    def get_supported_events(self):
        return ["ITEM_ADDED"]
    
    def handle_event(self, event_type, event_data):
        """Handle item added event and generate recommendations"""
        # Check if plugin is enabled
        from plugins.models import PluginConfiguration
        try:
            plugin_config = PluginConfiguration.objects.get(name=self.name)
            if not plugin_config.enabled:
                logger.info(f"[RECOMMENDER] Plugin disabled, skipping event {event_type}")
                return
        except PluginConfiguration.DoesNotExist:
            logger.warning(f"[RECOMMENDER] Plugin configuration not found, skipping event {event_type}")
            return
            
        if event_type == "ITEM_ADDED":
            self._handle_item_added(event_data)
    
    def _handle_item_added(self, event_data):
        """Process item addition and suggest recommendations"""
        try:
            product_id = event_data.get('product_id')
            basket_id = event_data.get('basket_id')
            
            logger.info(f"[RECOMMENDER] Processing item: {product_id} in basket: {basket_id}")
            
            # Get recommendations
            recommendations = self._get_recommendations(product_id)
            
            if recommendations:
                # Save recommendations to database
                for rec in recommendations:
                    Recommendation.objects.create(
                        basket_id=basket_id,
                        source_product_id=product_id,
                        recommended_product_id=rec['product_id'],
                        recommended_product_name=rec['name'],
                        recommended_price=float(rec['price']),
                        reason='Frequently bought together',
                        status='PENDING'
                    )
                
                # Publish recommendation event
                event_producer.publish(settings.KAFKA_TOPIC, {
                    'event_type': 'RECOMMENDATION_SUGGESTED',
                    'timestamp': timezone.now().isoformat(),
                    'basket_id': basket_id,
                    'source_product_id': product_id,
                    'recommendations': recommendations
                })
                
                logger.info(f"[RECOMMENDER] Suggested {len(recommendations)} items for {product_id}")
            else:
                logger.info(f"[RECOMMENDER] No recommendations found for {product_id}")
                
        except Exception as e:
            logger.error(f"[RECOMMENDER] Error processing recommendation: {e}")
    
    def _get_recommendations(self, product_id):
        """Get recommendations from DB or fallback to hardcoded rules"""
        # Try database rules first
        try:
            rules = RecommendationRule.objects.filter(
                source_product__product_id=product_id,
                is_active=True
            ).select_related('recommended_product').order_by('priority')
            
            if rules.exists():
                return [
                    {
                        'product_id': rule.recommended_product.product_id,
                        'name': rule.recommended_product.name,
                        'price': str(rule.recommended_product.price)
                    }
                    for rule in rules
                ]
        except Exception as e:
            logger.warning(f"[RECOMMENDER] DB lookup failed: {e}, using hardcoded rules")
        
        # Fallback to hardcoded rules
        return self.HARDCODED_RULES.get(product_id, [])
