from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from strawberry.django.views import GraphQLView as BaseGraphQLView


@method_decorator(csrf_exempt, name='dispatch')
class GraphQLView(BaseGraphQLView):
    def options(self, request, *args, **kwargs):
        """Handle CORS preflight requests"""
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response