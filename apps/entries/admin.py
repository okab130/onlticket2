from django.contrib import admin
from .models import Entry


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'gate', 'scanned_by', 'entered_at')
    list_filter = ('gate', 'entered_at')
    search_fields = ('ticket__ticket_number',)
    readonly_fields = ('entered_at',)
