from django.urls import path
from . import views

app_name = 'entries'

urlpatterns = [
    path('scan/', views.qr_scan_view, name='qr_scan'),
    path('verify/', views.verify_ticket_view, name='verify_ticket'),
    path('process/', views.process_entry, name='process_entry'),
    path('list/', views.entry_list, name='entry_list'),
    path('status/', views.entry_status_view, name='entry_status'),
]
