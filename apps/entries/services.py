"""入場管理サービス"""
from django.db import transaction
from django.db import models
from django.utils import timezone
from apps.entries.models import Entry
from apps.tickets.models import Ticket


def verify_and_record_entry(ticket_number: str, gate: str, scanned_by_user) -> dict:
    """
    チケット検証と入場記録
    
    Args:
        ticket_number: チケット番号
        gate: ゲート名
        scanned_by_user: スキャンしたスタッフ
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'ticket': Ticket or None,
            'entry': Entry or None
        }
    """
    try:
        # チケットを取得
        ticket = Ticket.objects.select_related(
            'order__event',
            'order__user',
            'seat__venue'
        ).get(ticket_number=ticket_number)
        
        # QRコード署名検証
        qr_service = TicketQRService()
        if not qr_service.verify_qr_code(ticket.qr_code):
            return {
                'success': False,
                'message': 'QRコードの検証に失敗しました。不正なチケットの可能性があります。',
                'ticket': ticket,
                'entry': None
            }
        
        # チケットステータス確認
        if ticket.status == 'cancelled':
            return {
                'success': False,
                'message': 'このチケットはキャンセルされています',
                'ticket': ticket,
                'entry': None
            }
        
        if ticket.status == 'used':
            # 既存の入場記録を取得
            existing_entry = Entry.objects.filter(ticket=ticket).first()
            return {
                'success': False,
                'message': f'このチケットは既に使用されています（入場日時: {existing_entry.entered_at.strftime("%Y年%m月%d日 %H:%M")}）',
                'ticket': ticket,
                'entry': existing_entry
            }
        
        # イベント日時チェック
        event = ticket.order.event
        now = timezone.now()
        
        # イベント開始24時間前から入場可能（例）
        if event.start_datetime > now + timezone.timedelta(hours=24):
            return {
                'success': False,
                'message': f'イベント開始前です。イベント開始: {event.start_datetime.strftime("%Y年%m月%d日 %H:%M")}',
                'ticket': ticket,
                'entry': None
            }
        
        # イベント終了後は入場不可
        if event.end_datetime and event.end_datetime < now:
            return {
                'success': False,
                'message': 'イベントは既に終了しています',
                'ticket': ticket,
                'entry': None
            }
        
        # 入場記録を作成
        with transaction.atomic():
            entry = Entry.objects.create(
                ticket=ticket,
                gate=gate,
                scanned_by=scanned_by_user
            )
            
            # チケットを使用済みに更新
            ticket.status = 'used'
            ticket.save(update_fields=['status'])
        
        return {
            'success': True,
            'message': '入場を許可しました',
            'ticket': ticket,
            'entry': entry
        }
        
    except Ticket.DoesNotExist:
        return {
            'success': False,
            'message': 'チケットが見つかりません',
            'ticket': None,
            'entry': None
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'エラーが発生しました: {str(e)}',
            'ticket': None,
            'entry': None
        }


def get_entry_statistics(event_id=None):
    """
    入場統計情報を取得
    
    Args:
        event_id: イベントID（指定時はそのイベントの統計、未指定時は全体）
        
    Returns:
        dict: 統計情報
    """
    queryset = Entry.objects.all()
    
    if event_id:
        queryset = queryset.filter(ticket__order__event_id=event_id)
    
    total_entries = queryset.count()
    today_entries = queryset.filter(
        entered_at__date=timezone.now().date()
    ).count()
    
    # ゲート別集計
    gate_stats = {}
    for entry in queryset.values('gate').annotate(count=models.Count('id')):
        gate_stats[entry['gate']] = entry['count']
    
    return {
        'total_entries': total_entries,
        'today_entries': today_entries,
        'gate_stats': gate_stats
    }
