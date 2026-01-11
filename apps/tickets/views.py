from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.db.models import Q
from apps.tickets.models import Ticket
from apps.orders.models import Order


@login_required
def my_tickets(request):
    """マイチケット一覧"""
    tickets = Ticket.objects.filter(
        order__user=request.user,
        status='valid'
    ).select_related('order__event', 'seat__venue').order_by('-created_at')
    
    return render(request, 'tickets/my_tickets.html', {
        'tickets': tickets
    })


@login_required
def ticket_detail(request, ticket_number):
    """チケット詳細（QRコード表示）"""
    ticket = get_object_or_404(
        Ticket.objects.select_related('order__event', 'seat__venue'),
        ticket_number=ticket_number,
        order__user=request.user
    )
    
    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket
    })


@login_required
def download_ticket_pdf(request, ticket_number):
    """チケットPDFダウンロード"""
    ticket = get_object_or_404(
        Ticket.objects.select_related('order__event', 'seat__venue'),
        ticket_number=ticket_number,
        order__user=request.user
    )
    
    # TODO: PDF生成機能の実装（reportlabを使用）
    # プロトタイプでは簡易実装
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket_number}.pdf"'
    response.write(b'PDF generation coming soon')
    
    return response


def validate_ticket(request, ticket_number):
    """
    チケット検証（入場ゲート用）
    スタッフ権限が必要
    """
    if not request.user.is_staff:
        raise Http404
    
    try:
        ticket = Ticket.objects.select_related('order__event', 'seat').get(
            ticket_number=ticket_number
        )
        
        # チケットの有効性をチェック
        if ticket.status != 'valid':
            return render(request, 'tickets/validation_result.html', {
                'ticket': ticket,
                'valid': False,
                'message': 'このチケットは無効です（使用済みまたはキャンセル済み）'
            })
        
        # 既に入場済みかチェック
        if ticket.entries.exists():
            return render(request, 'tickets/validation_result.html', {
                'ticket': ticket,
                'valid': False,
                'message': 'このチケットは既に使用されています'
            })
        
        return render(request, 'tickets/validation_result.html', {
            'ticket': ticket,
            'valid': True,
            'message': '入場可能です'
        })
        
    except Ticket.DoesNotExist:
        return render(request, 'tickets/validation_result.html', {
            'ticket': None,
            'valid': False,
            'message': 'チケットが見つかりません'
        })
