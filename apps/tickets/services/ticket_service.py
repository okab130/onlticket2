"""
チケット関連のサービスロジック
"""
import qrcode
import hmac
import hashlib
import uuid
from io import BytesIO
from django.core.files import File
from django.db import transaction
from django.conf import settings
from apps.tickets.models import Ticket
from apps.orders.models import Order


class TicketQRService:
    """QRコード生成・検証サービス"""
    
    @staticmethod
    def generate_ticket_number():
        """一意なチケット番号を生成"""
        return f"TKT{uuid.uuid4().hex[:12].upper()}"
    
    @staticmethod
    def generate_signature(ticket_number):
        """チケット番号の署名を生成（HMAC-SHA256）"""
        secret_key = getattr(settings, 'SECRET_KEY', 'default-secret-key')
        signature = hmac.new(
            secret_key.encode(),
            ticket_number.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        return signature
    
    @staticmethod
    def generate_qr_code(ticket_number):
        """QRコードを生成"""
        signature = TicketQRService.generate_signature(ticket_number)
        qr_data = f"{ticket_number}:{signature}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return File(buffer, name=f'{ticket_number}.png')
    
    @staticmethod
    def verify_qr_code(qr_data):
        """QRコードを検証"""
        try:
            parts = qr_data.split(':')
            if len(parts) != 2:
                return False, "無効なQRコード形式"
            
            ticket_number, signature = parts
            expected_signature = TicketQRService.generate_signature(ticket_number)
            
            if signature != expected_signature:
                return False, "署名が無効です"
            
            return True, ticket_number
        except Exception as e:
            return False, str(e)


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
