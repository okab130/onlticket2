from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from apps.entries.models import Entry
from apps.tickets.models import Ticket


@staff_member_required
def scan_qr(request):
    """QRコードスキャン画面（スタッフ用）"""
    return render(request, 'entries/scan_qr.html')


@staff_member_required
def process_entry(request):
    """入場処理"""
    if request.method == 'POST':
        ticket_number = request.POST.get('ticket_number', '').strip()
        gate = request.POST.get('gate', 'メインゲート')
        
        try:
            ticket = Ticket.objects.select_related('order__event', 'seat').get(
                ticket_number=ticket_number
            )
            
            # チケットの有効性チェック
            if ticket.status != 'valid':
                return render(request, 'entries/entry_result.html', {
                    'success': False,
                    'message': 'このチケットは無効です',
                    'ticket': ticket
                })
            
            # 既に入場済みかチェック
            existing_entry = Entry.objects.filter(ticket=ticket).first()
            if existing_entry:
                return render(request, 'entries/entry_result.html', {
                    'success': False,
                    'message': f'このチケットは既に使用されています（入場日時: {existing_entry.entered_at.strftime("%Y-%m-%d %H:%M")}）',
                    'ticket': ticket
                })
            
            # 入場記録を作成
            with transaction.atomic():
                entry = Entry.objects.create(
                    ticket=ticket,
                    gate=gate,
                    scanned_by=request.user
                )
                
                # チケットを使用済みに更新
                ticket.status = 'used'
                ticket.save()
            
            return render(request, 'entries/entry_result.html', {
                'success': True,
                'message': '入場を許可しました',
                'ticket': ticket,
                'entry': entry
            })
            
        except Ticket.DoesNotExist:
            return render(request, 'entries/entry_result.html', {
                'success': False,
                'message': 'チケットが見つかりません',
                'ticket_number': ticket_number
            })
    
    return redirect('entries:scan_qr')


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
