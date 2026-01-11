from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'order', 'seat', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ticket_number', 'order__order_number')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at')
