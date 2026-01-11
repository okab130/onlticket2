from django.urls import path
from . import views

app_name = 'seats'

urlpatterns = [
    path('<int:venue_id>/', views.SeatListView.as_view(), name='seat_list'),
    path('<int:venue_id>/create/', views.SeatBulkCreateView.as_view(), name='seat_bulk_create'),
    path('delete/<int:pk>/', views.SeatDeleteView.as_view(), name='seat_delete'),
    path('select/<int:event_id>/<int:ticket_type_id>/', views.SeatSelectionView.as_view(), name='seat_selection'),
]
