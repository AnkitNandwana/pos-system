import strawberry
from django.utils import timezone
from baskets.models import Basket
from events.producer import event_producer
from django.conf import settings


@strawberry.type
class IdentifyCustomerResponse:
    success: bool
    message: str
    basket_id: str


@strawberry.type
class CustomerMutations:
    @strawberry.mutation
    def identify_customer(self, basket_id: str, customer_identifier: str) -> IdentifyCustomerResponse:
        try:
            basket = Basket.objects.get(basket_id=basket_id)
            
            # Publish event
            event_producer.publish(settings.KAFKA_TOPIC, {
                'event_type': 'CUSTOMER_IDENTIFIED',
                'timestamp': timezone.now().isoformat(),
                'basket_id': basket_id,
                'customer_identifier': customer_identifier
            })
            
            return IdentifyCustomerResponse(
                success=True,
                message=f"Customer identification initiated for {customer_identifier}",
                basket_id=basket_id
            )
        except Basket.DoesNotExist:
            return IdentifyCustomerResponse(
                success=False,
                message=f"Basket {basket_id} not found",
                basket_id=basket_id
            )
