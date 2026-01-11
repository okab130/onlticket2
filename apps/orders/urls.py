from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='cart_add'),
    path('cart/add-free/', views.add_to_cart_free_view, name='add_to_cart_free'),
    path('cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='cart_remove'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('complete/<str:order_number>/', views.PurchaseCompleteView.as_view(), name='purchase_complete'),
    path('cancellation/request/<int:order_id>/', views.cancellation_request_view, name='cancellation_request'),
]
