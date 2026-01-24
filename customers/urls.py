from django.urls import path
from .views import MockCustomerLookupView

urlpatterns = [
    path('mock-customer-lookup/<str:identifier>/', MockCustomerLookupView.as_view(), name='mock_customer_lookup'),
]
