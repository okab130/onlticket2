"""会員管理URL設定"""
from django.urls import path
from apps.members import views

app_name = 'members'

urlpatterns = [
    # 会員登録・ログイン
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # マイページ
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # 購入履歴
    path('purchase-history/', views.purchase_history_view, name='purchase_history'),
    
    # パスワード変更
    path('password/change/', views.password_change_view, name='password_change'),
    
    # パスワードリセット
    path('password/reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password/reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
]
