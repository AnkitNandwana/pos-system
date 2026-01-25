import json
import time
from decimal import Decimal
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from plugins.purchase_recommender.models import Recommendation


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def recommendation_stream(request, basket_id):
    """Server-Sent Events stream for real-time recommendations"""
    
    def event_stream():
        while True:
            # Get pending recommendations
            recommendations = list(Recommendation.objects.filter(
                basket_id=basket_id,
                status='PENDING'
            ).values(
                'id', 'recommended_product_id', 'recommended_product_name',
                'recommended_price', 'reason', 'status'
            ))
            
            # Send data
            data = json.dumps({
                'type': 'recommendations',
                'recommendations': recommendations,
                'timestamp': time.time()
            }, cls=DecimalEncoder)
            
            yield f"data: {data}\n\n"
            
            time.sleep(2)  # Check every 2 seconds
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'Cache-Control'
    
    return response