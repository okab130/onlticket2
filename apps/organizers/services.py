"""主催者サービス - 売上集計・分析機能"""
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order
from apps.events.models import Event


def calculate_sales_summary(organizer):
    """
    売上サマリーを計算
    
    Args:
        organizer: 主催者オブジェクト
        
    Returns:
        dict: {
            'total_sales': 総売上,
            'total_tickets': 販売枚数,
            'total_events': イベント数,
            'sold_out_events': 完売イベント数,
            'active_events': 開催予定イベント数
        }
    """
    events = Event.objects.filter(organizer=organizer)
    
    # 総売上と販売枚数
    sales_data = Order.objects.filter(
        event__organizer=organizer,
        status='completed'
    ).aggregate(
        total_sales=Sum('total_amount'),
        total_tickets=Count('tickets')
    )
    
    # 完売イベント数（全チケットタイプが売り切れ）
    sold_out_count = 0
    for event in events:
        ticket_types = event.ticket_types.all()
        if ticket_types and all(tt.sold_quantity >= tt.total_quantity for tt in ticket_types):
            sold_out_count += 1
    
    # 開催予定イベント数（未来のイベント）
    active_events_count = events.filter(start_datetime__gte=timezone.now()).count()
    
    return {
        'total_sales': sales_data['total_sales'] or 0,
        'total_tickets': sales_data['total_tickets'] or 0,
        'total_events': events.count(),
        'sold_out_events': sold_out_count,
        'active_events': active_events_count,
    }


def get_sales_trend(organizer, days=30):
    """
    販売推移データを取得（直近N日間の日次売上）
    
    Args:
        organizer: 主催者オブジェクト
        days: 取得日数（デフォルト30日）
        
    Returns:
        list: [{
            'date': 日付,
            'sales': 売上,
            'tickets': 販売枚数
        }, ...]
    """
    start_date = timezone.now() - timedelta(days=days)
    
    # 日次売上を集計
    daily_sales = Order.objects.filter(
        event__organizer=organizer,
        status='completed',
        created_at__gte=start_date
    ).extra(
        select={'day': 'DATE(created_at)'}
    ).values('day').annotate(
        sales=Sum('total_amount'),
        tickets=Count('tickets')
    ).order_by('day')
    
    return [
        {
            'date': item['day'].strftime('%Y-%m-%d'),
            'sales': float(item['sales']),
            'tickets': item['tickets']
        }
        for item in daily_sales
    ]


def get_event_sales(organizer):
    """
    イベント別売上を取得
    
    Args:
        organizer: 主催者オブジェクト
        
    Returns:
        list: イベント別売上データ
    """
    events = Event.objects.filter(organizer=organizer).prefetch_related('orders')
    
    event_sales = []
    for event in events:
        orders = event.orders.filter(status='completed')
        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_tickets = sum(order.tickets.count() for order in orders)
        
        event_sales.append({
            'event': event,
            'total_sales': total_sales,
            'total_tickets': total_tickets,
        })
    
    return sorted(event_sales, key=lambda x: x['total_sales'], reverse=True)
