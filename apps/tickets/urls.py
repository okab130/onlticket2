from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('<str:ticket_number>/', views.ticket_detail, name='ticket_detail'),
    path('<str:ticket_number>/pdf/', views.download_ticket_pdf, name='download_pdf'),
    path('<str:ticket_number>/validate/', views.validate_ticket, name='validate'),
]
