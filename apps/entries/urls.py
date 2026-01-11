from django.urls import path
from . import views

app_name = 'entries'

urlpatterns = [
    path('scan/', views.scan_qr, name='scan_qr'),
    path('process/', views.process_entry, name='process_entry'),
    path('list/', views.entry_list, name='entry_list'),
]
