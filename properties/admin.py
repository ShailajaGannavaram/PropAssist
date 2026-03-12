from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'city', 'price', 'is_available']
    search_fields = ['title', 'city', 'location']
    list_filter = ['property_type', 'city', 'is_available']

