from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Seed sample products for testing'
    
    def handle(self, *args, **options):
        products = [
            {'product_id': 'BURGER', 'name': 'Cheeseburger', 'price': 8.99, 'category': 'food'},
            {'product_id': 'FRIES', 'name': 'French Fries', 'price': 2.99, 'category': 'food'},
            {'product_id': 'COKE', 'name': 'Coca Cola', 'price': 1.99, 'category': 'beverage'},
            {'product_id': 'COFFEE', 'name': 'Coffee', 'price': 3.99, 'category': 'beverage'},
            {'product_id': 'DONUT', 'name': 'Donut', 'price': 1.99, 'category': 'food'},
            {'product_id': 'MUFFIN', 'name': 'Blueberry Muffin', 'price': 2.49, 'category': 'food'},
            {'product_id': 'LAPTOP', 'name': 'Laptop Computer', 'price': 999.99, 'category': 'electronics'},
            {'product_id': 'MOUSE', 'name': 'Wireless Mouse', 'price': 29.99, 'category': 'electronics'},
            {'product_id': 'LAPTOP_BAG', 'name': 'Laptop Bag', 'price': 39.99, 'category': 'accessories'},
            {'product_id': 'PHONE', 'name': 'Smartphone', 'price': 699.99, 'category': 'electronics'},
            {'product_id': 'PHONE_CASE', 'name': 'Phone Case', 'price': 19.99, 'category': 'accessories'},
            {'product_id': 'SCREEN_PROTECTOR', 'name': 'Screen Protector', 'price': 9.99, 'category': 'accessories'},
            {'product_id': 'PIZZA', 'name': 'Pizza', 'price': 12.99, 'category': 'food'},
            {'product_id': 'GARLIC_BREAD', 'name': 'Garlic Bread', 'price': 4.99, 'category': 'food'},
            {'product_id': 'SODA', 'name': 'Soda', 'price': 2.49, 'category': 'beverage'},
            # Age-restricted products
            {'product_id': 'BEER', 'name': 'Beer', 'price': 4.99, 'category': 'alcohol', 'age_restricted': True, 'minimum_age': 21},
            {'product_id': 'WINE', 'name': 'Wine', 'price': 12.99, 'category': 'alcohol', 'age_restricted': True, 'minimum_age': 21},
            {'product_id': 'CIGARETTES', 'name': 'Cigarettes', 'price': 8.99, 'category': 'tobacco', 'age_restricted': True, 'minimum_age': 18},
            {'product_id': 'ENERGY_DRINK', 'name': 'Energy Drink', 'price': 3.99, 'category': 'beverage', 'age_restricted': True, 'minimum_age': 16},
        ]
        
        created_count = 0
        for p in products:
            product, created = Product.objects.get_or_create(
                product_id=p['product_id'],
                defaults=p
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created: {product.name}")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Seeded {created_count} products!'))
