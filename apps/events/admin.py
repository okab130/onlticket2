from django.contrib import admin
from .models import Venue, Event, TicketType


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'capacity', 'created_at']
    search_fields = ['name', 'address']
    list_filter = ['created_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'venue', 'start_datetime', 'is_public', 'status']
    list_filter = ['category', 'is_public', 'status', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_datetime'


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'type', 'price', 'sold_quantity', 'total_quantity']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'event__name']

