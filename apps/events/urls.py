from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # 購入者向けイベント
    path('', views.PublicEventListView.as_view(), name='public_event_list'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='public_event_detail'),
    
    # 会場管理（主催者）
    path('venues/', views.VenueListView.as_view(), name='venue_list'),
    path('venues/create/', views.VenueCreateView.as_view(), name='venue_create'),
    path('venues/<int:pk>/edit/', views.VenueUpdateView.as_view(), name='venue_update'),
    path('venues/<int:pk>/delete/', views.VenueDeleteView.as_view(), name='venue_delete'),
    
    # イベント管理（主催者）
    path('manage/', views.EventListView.as_view(), name='event_list'),
    path('manage/create/', views.EventCreateView.as_view(), name='event_create'),
    path('manage/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('manage/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    
    # チケット種別管理（主催者）
    path('manage/<int:event_id>/ticket-types/create/', views.TicketTypeCreateView.as_view(), name='tickettype_create'),
    path('manage/ticket-types/<int:pk>/edit/', views.TicketTypeUpdateView.as_view(), name='tickettype_update'),
    path('manage/ticket-types/<int:pk>/delete/', views.TicketTypeDeleteView.as_view(), name='tickettype_delete'),
]
