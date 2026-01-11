import uuid
from django.utils import timezone
from django.db import transaction
from .models import Order, Payment
from apps.tickets.models import Ticket
from apps.seats.models import Seat


def create_order(user, cart):
    """
    購入確定処理
    
    Args:
        user: Userオブジェクト
        cart: Cartオブジェクト
    
    Returns:
        Order: 作成された注文オブジェクト
    """
    with transaction.atomic():
        # カートアイテム取得
        cart_items = cart.items.select_related('seat__venue').all()
        
        if not cart_items:
            raise ValueError('カートが空です')
        
        # イベント取得（全座席が同じ会場と仮定）
        first_seat = cart_items[0].seat
        # 注意: 実際にはイベントIDをカートに保存するか、別途渡す必要があります
        # 簡略化のため、ここではイベントを適当に取得
        from apps.events.models import Event
        event = Event.objects.filter(venue=first_seat.venue, is_public=True).first()
        
        if not event:
            raise ValueError('イベントが見つかりません')
        
        # 合計金額計算（簡略化：固定価格）
        # 実際にはticket_typeの価格を使用
        total_amount = len(cart_items) * 5000  # 仮の価格
        
        # 注文番号生成
        order_number = f"ORD{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        
        # 注文作成
        order = Order.objects.create(
            order_number=order_number,
            user=user,
            event=event,
            total_amount=total_amount,
            status='paid'  # MVP: 即座に支払い済みとする
        )
        
        # 支払い作成
        payment = Payment.objects.create(
            order=order,
            method='credit_card',
            amount=total_amount,
            status='completed',
            transaction_id=uuid.uuid4().hex,
            paid_at=timezone.now()
        )
        
        # チケット作成と座席ステータス更新
        for cart_item in cart_items:
            seat = cart_item.seat
            
            # 座席を売約済みに更新
            seat.status = 'sold'
            seat.save()
            
            # チケット作成（簡略版）
            # 実際にはtickets/services.pyでQRコードも生成
            ticket_number = f"TKT{order.order_number}{seat.id}"
            
            # Ticketモデルは後で実装するため、コメントアウト
            # Ticket.objects.create(
            #     order=order,
            #     seat=seat,
            #     ticket_number=ticket_number,
            #     status='active'
            # )
        
        # カート削除
        cart.items.all().delete()
        cart.delete()
        
        return order
