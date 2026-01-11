from django.db import models
from apps.events.models import Venue
from apps.members.models import User


class Seat(models.Model):
    """座席モデル"""
    
    STATUS_CHOICES = [
        ('available', '空席'),
        ('reserved', '予約中'),
        ('sold', '売約済'),
    ]
    
    SEAT_TYPE_CHOICES = [
        ('S', 'S席'),
        ('A', 'A席'),
        ('B', 'B席'),
    ]
    
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='seats', verbose_name='会場')
    
    # 座席情報
    block = models.CharField('ブロック', max_length=50)
    row = models.CharField('列', max_length=10)
    number = models.CharField('番号', max_length=10)
    seat_type = models.CharField('座席種別', max_length=1, choices=SEAT_TYPE_CHOICES)
    
    # ステータス
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='available')
    
    # 仮予約情報
    reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='reserved_seats', verbose_name='仮予約者')
    reserved_at = models.DateTimeField('仮予約日時', null=True, blank=True)
    
    # 楽観的ロック用
    version = models.IntegerField('バージョン', default=0)
    
    # タイムスタンプ
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'seats'
        verbose_name = '座席'
        verbose_name_plural = '座席'
        unique_together = [['venue', 'block', 'row', 'number']]
        indexes = [
            models.Index(fields=['venue', 'status'], name='idx_seats_venue_status'),
            models.Index(fields=['status', 'reserved_at'], name='idx_seats_status_reserved_at'),
        ]
    
    def __str__(self):
        return f"{self.venue.name} {self.block}-{self.row}-{self.number}"

