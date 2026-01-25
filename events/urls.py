from django.urls import path
from . import views

urlpatterns = [
    path('recommendations/<str:basket_id>/', views.recommendation_stream, name='recommendation_stream'),
]