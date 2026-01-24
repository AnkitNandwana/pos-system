from django.contrib import admin
from .models import PluginConfiguration


@admin.register(PluginConfiguration)
class PluginConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled', 'created_at', 'updated_at']
    list_filter = ['enabled']
    search_fields = ['name', 'description']
