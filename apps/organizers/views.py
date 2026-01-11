"""主催者ビュー - ダッシュボード、売上管理"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from apps.organizers.models import Organizer
from apps.organizers.services import calculate_sales_summary, get_sales_trend, get_event_sales
from apps.orders.models import Cancellation
import csv


@login_required
def dashboard_view(request):
    """主催者ダッシュボード"""
    try:
        organizer = request.user.organizer
    except Organizer.DoesNotExist:
        messages.error(request, '主催者アカウントが見つかりません。')
        return redirect('home')
    
    # 売上サマリー
    summary = calculate_sales_summary(organizer)
    
    # 販売推移（直近30日）
    sales_trend = get_sales_trend(organizer, days=30)
    
    # グラフ用データ（JSON形式）
    trend_labels = [item['date'] for item in sales_trend]
    trend_sales = [item['sales'] for item in sales_trend]
    trend_tickets = [item['tickets'] for item in sales_trend]
    
    context = {
        'organizer': organizer,
        'summary': summary,
        'trend_labels': trend_labels,
        'trend_sales': trend_sales,
        'trend_tickets': trend_tickets,
    }
    
    return render(request, 'organizers/dashboard.html', context)


@login_required
def sales_report_view(request):
    """売上レポート"""
    try:
        organizer = request.user.organizer
    except Organizer.DoesNotExist:
        messages.error(request, '主催者アカウントが見つかりません。')
        return redirect('home')
    
    # イベント別売上
    event_sales = get_event_sales(organizer)
    
    context = {
        'organizer': organizer,
        'event_sales': event_sales,
    }
    
    return render(request, 'organizers/sales_report.html', context)


@login_required
def sales_report_csv_view(request):
    """売上レポートCSV出力"""
    try:
        organizer = request.user.organizer
    except Organizer.DoesNotExist:
        messages.error(request, '主催者アカウントが見つかりません。')
        return redirect('home')

    # イベント別売上
    event_sales = get_event_sales(organizer)

    # CSV生成
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['イベント名', '開催日', '売上', '販売枚数'])

    for item in event_sales:
        writer.writerow([
            item['event'].name,
            item['event'].start_datetime.strftime('%Y-%m-%d %H:%M'),
            item['total_sales'],
            item['total_tickets'],
        ])

    return response


@login_required
def cancellation_list_view(request):
    """キャンセル申請一覧"""
    try:
        organizer = request.user.organizer
    except Organizer.DoesNotExist:
        messages.error(request, '主催者アカウントが見つかりません。')
        return redirect('home')
    
    # 主催者のイベントに関するキャンセル申請を取得
    cancellations = Cancellation.objects.filter(
        order__event__organizer=organizer
    ).select_related('order__user', 'order__event').order_by('-requested_at')
    
    return render(request, 'organizers/cancellation_list.html', {
        'cancellations': cancellations,
    })


@login_required
def cancellation_approval_view(request, cancellation_id):
    """キャンセル承認・却下"""
    try:
        organizer = request.user.organizer
    except Organizer.DoesNotExist:
        messages.error(request, '主催者アカウントが見つかりません。')
        return redirect('home')
    
    cancellation = get_object_or_404(
        Cancellation,
        pk=cancellation_id,
        order__event__organizer=organizer
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            from apps.orders.services import process_cancellation
            try:
                process_cancellation(cancellation, approved_by=request.user)
                messages.success(request, 'キャンセルを承認しました。')
            except Exception as e:
                messages.error(request, f'キャンセル処理に失敗しました: {str(e)}')
        
        elif action == 'reject':
            cancellation.status = 'rejected'
            cancellation.processed_at = timezone.now()
            cancellation.processed_by = request.user
            cancellation.save()
            messages.success(request, 'キャンセル申請を却下しました。')
        
        return redirect('organizers:cancellation_list')
    
    return render(request, 'organizers/cancellation_detail.html', {
        'cancellation': cancellation,
    })
