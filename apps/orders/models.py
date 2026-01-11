from django.db import models
from django.conf import settings
from apps.events.models import Event
from apps.seats.models import Seat


class Cart(models.Model):
    """カートモデル"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cart #{self.id} - {self.user.username}"
    
    @property
    def total_amount(self):
        """カート内の合計金額"""
        return sum(item.seat.get_price() for item in self.items.all())
    
    @property
    def item_count(self):
        """カート内のアイテム数"""
        return self.items.count()


class CartItem(models.Model):
    """カートアイテムモデル"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'seat']
        ordering = ['added_at']
    
    def __str__(self):
        return f"{self.cart.user.username} - {self.seat}"


class Order(models.Model):
    """注文モデル"""
    STATUS_CHOICES = [
        ('pending', '支払待ち'),
        ('paid', '支払済み'),
        ('cancelled', 'キャンセル'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"


class Payment(models.Model):
    """支払モデル"""
    METHOD_CHOICES = [
        ('credit_card', 'クレジットカード'),
        ('convenience_store', 'コンビニ決済'),
        ('bank_transfer', '銀行振込'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '未払い'),
        ('completed', '完了'),
        ('failed', '失敗'),
        ('refunded', '返金済み'),
    ]
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment #{self.id} - {self.order.order_number}"

