from django.db import models
from apps.orders.models import Order
from apps.seats.models import Seat


class Ticket(models.Model):
    """チケットモデル"""
    
    STATUS_CHOICES = [
        ('valid', '有効'),
        ('used', '使用済み'),
        ('cancelled', 'キャンセル済み'),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='注文'
    )
    seat = models.ForeignKey(
        Seat,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name='座席'
    )
    
    ticket_number = models.CharField('チケット番号', max_length=16, unique=True)
    qr_code = models.ImageField('QRコード', upload_to='tickets/qr_codes/', blank=True)
    
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='valid')
    
    created_at = models.DateTimeField('発行日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'tickets'
        verbose_name = 'チケット'
        verbose_name_plural = 'チケット'
        indexes = [
            models.Index(fields=['ticket_number'], name='idx_tickets_ticket_number'),
            models.Index(fields=['order'], name='idx_tickets_order'),
            models.Index(fields=['status'], name='idx_tickets_status'),
        ]
    
    def __str__(self):
        return f"Ticket {self.ticket_number}"
    
    def generate_ticket_number(self):
        """チケット番号を生成"""
        import uuid
        return f"TK{uuid.uuid4().hex[:14].upper()}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)
