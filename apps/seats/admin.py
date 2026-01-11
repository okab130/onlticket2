from django.contrib import admin
from .models import Seat


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['venue', 'block', 'row', 'number', 'seat_type', 'status']
    list_filter = ['venue', 'seat_type', 'status', 'created_at']
    search_fields = ['block', 'row', 'number']

