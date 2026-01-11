"""主催者URL設定"""
from django.urls import path
from apps.organizers import views

app_name = 'organizers'

urlpatterns = [
    # ダッシュボード
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # 売上レポート
    path('sales-report/', views.sales_report_view, name='sales_report'),
    path('sales-report/csv/', views.sales_report_csv_view, name='sales_report_csv'),
    
    # キャンセル管理
    path('cancellations/', views.cancellation_list_view, name='cancellation_list'),
    path('cancellations/<int:cancellation_id>/', views.cancellation_approval_view, name='cancellation_approval'),
]
