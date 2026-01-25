from django.contrib import admin
from django.urls import path, include
from config.graphql_view import GraphQLView
from schema import schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', GraphQLView.as_view(schema=schema)),
    path('api/', include('customers.urls')),
    path('events/', include('events.urls')),
]
