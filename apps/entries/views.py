from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.entries.models import Entry
from apps.tickets.models import Ticket
from apps.entries.services import verify_and_record_entry, get_entry_statistics


@staff_member_required
def qr_scan_view(request):
    """QRコードスキャン画面（スタッフ用）"""
    return render(request, 'entries/qr_scan.html')


@staff_member_required
def scan_qr(request):
    """QRコードスキャン画面（旧版、互換性のため残す）"""
    return redirect('entries:qr_scan')


@staff_member_required
@require_http_methods(["POST"])
def verify_ticket_view(request):
    """
    チケット検証API（Ajax用）
    
    POST data:
        - ticket_number: チケット番号
        - gate: ゲート名（オプション、デフォルト: メインゲート）
    """
    ticket_number = request.POST.get('ticket_number', '').strip()
    gate = request.POST.get('gate', 'メインゲート')
    
    if not ticket_number:
        return JsonResponse({
            'success': False,
            'message': 'チケット番号を入力してください'
        })
    
    # サービスを呼び出して検証・入場記録
    result = verify_and_record_entry(ticket_number, gate, request.user)
    
    # JSON形式でレスポンスを返す
    response_data = {
        'success': result['success'],
        'message': result['message'],
    }
    
    if result['ticket']:
        ticket = result['ticket']
        response_data['ticket'] = {
            'ticket_number': ticket.ticket_number,
            'event_name': ticket.order.event.name,
            'seat_info': f"{ticket.seat.block} {ticket.seat.row}列 {ticket.seat.number}番" if ticket.seat else "自由席",
            'ticket_type': ticket.order.event.tickettype_set.first().name if ticket.order.event.tickettype_set.exists() else "一般",
        }
    
    if result['entry']:
        entry = result['entry']
        response_data['entry'] = {
            'entered_at': entry.entered_at.strftime('%Y年%m月%d日 %H:%M:%S'),
            'gate': entry.gate,
        }
    
    return JsonResponse(response_data)


@staff_member_required
def process_entry(request):
    """入場処理（フォーム送信用、旧版）"""
    if request.method == 'POST':
        ticket_number = request.POST.get('ticket_number', '').strip()
        gate = request.POST.get('gate', 'メインゲート')
        
        result = verify_and_record_entry(ticket_number, gate, request.user)
        
        return render(request, 'entries/entry_result.html', {
            'success': result['success'],
            'message': result['message'],
            'ticket': result['ticket'],
            'entry': result['entry']
        })
    
    return redirect('entries:qr_scan')


@staff_member_required
def entry_list(request):
    """入場記録一覧"""
    entries = Entry.objects.select_related(
        'ticket__order__event',
        'ticket__seat',
        'scanned_by'
    ).order_by('-entered_at')[:100]
    
    # 統計情報
    total_entries = Entry.objects.count()
    today_entries = Entry.objects.filter(
        entered_at__date=timezone.now().date()
    ).count()
    
    return render(request, 'entries/entry_list.html', {
        'entries': entries,
        'total_entries': total_entries,
        'today_entries': today_entries
    })


@staff_member_required
def entry_status_view(request):
    """入場状況リアルタイム表示"""
    event_id = request.GET.get('event_id')
    
    # 統計情報を取得
    stats = get_entry_statistics(event_id)
    
    # 最近の入場記録
    recent_entries = Entry.objects.select_related(
        'ticket__order__event',
        'ticket__seat',
        'scanned_by'
    ).order_by('-entered_at')[:20]
    
    if event_id:
        recent_entries = recent_entries.filter(ticket__order__event_id=event_id)
    
    return render(request, 'entries/entry_status.html', {
        'stats': stats,
        'recent_entries': recent_entries,
        'event_id': event_id
    })
