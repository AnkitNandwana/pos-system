from django.core.management.base import BaseCommand
from products.models import Product
from plugins.models import PluginConfiguration


class Command(BaseCommand):
    help = 'Setup age verification plugin with sample age-restricted products'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up Age Verification Plugin...')
        
        # Create plugin configuration
        config, created = PluginConfiguration.objects.get_or_create(
            name='age_verification',
            defaults={
                'enabled': True,
                'description': 'Enforces age verification for restricted products',
                'config': {
                    'default_verification_method': 'ID_SCAN',
                    'strict_enforcement': True
                }
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Plugin configuration created'))
        else:
            self.stdout.write('✓ Plugin configuration already exists')
        
        # Sample age-restricted products
        sample_products = [
            {
                'product_id': 'WINE-001',
                'name': 'Red Wine Bottle',
                'price': 25.99,
                'category': 'alcohol',
                'age_restricted': True,
                'minimum_age': 21,
                'age_restriction_category': 'alcohol'
            },
            {
                'product_id': 'BEER-001',
                'name': 'Beer 6-Pack',
                'price': 12.99,
                'category': 'alcohol',
                'age_restricted': True,
                'minimum_age': 21,
                'age_restriction_category': 'alcohol'
            },
            {
                'product_id': 'TOBACCO-001',
                'name': 'Cigarettes',
                'price': 8.99,
                'category': 'tobacco',
                'age_restricted': True,
                'minimum_age': 18,
                'age_restriction_category': 'tobacco'
            },
            {
                'product_id': 'ENERGY-001',
                'name': 'Energy Drink',
                'price': 3.99,
                'category': 'beverages',
                'age_restricted': True,
                'minimum_age': 16,
                'age_restriction_category': 'energy'
            },
            {
                'product_id': 'SODA-001',
                'name': 'Regular Soda',
                'price': 1.99,
                'category': 'beverages',
                'age_restricted': False,
                'minimum_age': None,
                'age_restriction_category': None
            }
        ]
        
        created_count = 0
        for product_data in sample_products:
            product, created = Product.objects.get_or_create(
                product_id=product_data['product_id'],
                defaults=product_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_count} new products'))
        
        # Summary
        total_products = Product.objects.count()
        restricted_products = Product.objects.filter(age_restricted=True).count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('AGE VERIFICATION SETUP COMPLETE')
        self.stdout.write('='*50)
        self.stdout.write(f'Total products: {total_products}')
        self.stdout.write(f'Age-restricted products: {restricted_products}')
        self.stdout.write(f'Plugin enabled: {config.enabled}')
        self.stdout.write('\nAge-restricted products:')
        
        for product in Product.objects.filter(age_restricted=True):
            self.stdout.write(f'  • {product.name} (min age: {product.minimum_age})')
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Run migrations: python manage.py migrate')
        self.stdout.write('2. Start Kafka consumer: python manage.py consume_events')
        self.stdout.write('3. Test with: python test_age_verification.py')