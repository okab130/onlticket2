"""
チケット関連のサービスロジック
"""
import qrcode
from io import BytesIO
from django.core.files import File
from django.db import transaction
from apps.tickets.models import Ticket
from apps.orders.models import Order


def generate_qr_code_image(ticket_number):
    """
    チケット番号からQRコード画像を生成
    
    Args:
        ticket_number: チケット番号
        
    Returns:
        File: QRコード画像ファイル
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(ticket_number)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return File(buffer, name=f'{ticket_number}.png')


@transaction.atomic
def create_tickets_for_order(order_id):
    """
    注文に対してチケットを生成する
    
    Args:
        order_id: 注文ID
        
    Returns:
        list: 生成されたチケットのリスト
    """
    order = Order.objects.select_related('event').prefetch_related('cart__items__seat').get(id=order_id)
    
    tickets = []
    
    # カート内の各座席に対してチケットを作成
    cart = order.user.carts.filter(event=order.event).first()
    if cart:
        for cart_item in cart.items.all():
            ticket = Ticket.objects.create(
                order=order,
                seat=cart_item.seat
            )
            
            # QRコード生成
            qr_image = generate_qr_code_image(ticket.ticket_number)
            ticket.qr_code.save(f'{ticket.ticket_number}.png', qr_image, save=True)
            
            # 座席ステータスを売約済に更新
            seat = cart_item.seat
            seat.status = 'sold'
            seat.reserved_by = None
            seat.reserved_at = None
            seat.save()
            
            tickets.append(ticket)
    
    return tickets


def cancel_ticket(ticket_id):
    """
    チケットをキャンセルする
    
    Args:
        ticket_id: チケットID
    """
    with transaction.atomic():
        ticket = Ticket.objects.select_related('seat').get(id=ticket_id)
        
        # チケットステータスを更新
        ticket.status = 'cancelled'
        ticket.save()
        
        # 座席を空席に戻す
        if ticket.seat:
            ticket.seat.status = 'available'
            ticket.seat.save()
