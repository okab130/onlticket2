from django.db import models


class Venue(models.Model):
    """会場モデル"""
    
    name = models.CharField('会場名', max_length=200)
    address = models.TextField('住所')
    capacity = models.IntegerField('収容人数')
    
    # 座席図画像（オプション）
    seat_map_image = models.ImageField('座席図', upload_to='venue_seat_maps/', blank=True, null=True)
    
    # タイムスタンプ
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'venues'
        verbose_name = '会場'
        verbose_name_plural = '会場'
        indexes = [
            models.Index(fields=['name'], name='idx_venues_name'),
        ]
    
    def __str__(self):
        return self.name


class Event(models.Model):
    """イベントモデル"""
    
    CATEGORY_CHOICES = [
        ('concert', 'コンサート・ライブ'),
        ('sports', 'スポーツ観戦'),
        ('theater', '演劇・舞台'),
        ('festival', 'フェス・野外イベント'),
        ('online', 'オンラインイベント'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '販売準備中'),
        ('on_sale', '販売中'),
        ('paused', '販売一時停止'),
        ('sold_out', '売り切れ'),
        ('closed', '販売終了'),
        ('cancelled', '開催中止'),
    ]
    
    # 基本情報
    name = models.CharField('イベント名', max_length=200)
    description = models.TextField('説明')
    category = models.CharField('カテゴリ', max_length=20, choices=CATEGORY_CHOICES)
    
    # 画像
    image = models.ImageField('イベント画像', upload_to='event_images/', blank=True, null=True)
    
    # 開催情報
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name='events', verbose_name='会場')
    start_datetime = models.DateTimeField('開始日時')
    end_datetime = models.DateTimeField('終了日時', null=True, blank=True)
    
    # 主催者
    organizer = models.ForeignKey('organizers.Organizer', on_delete=models.CASCADE, related_name='events', verbose_name='主催者')
    
    # ステータス
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField('公開', default=False)
    
    # タイムスタンプ
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'events'
        verbose_name = 'イベント'
        verbose_name_plural = 'イベント'
        indexes = [
            models.Index(fields=['is_public', 'start_datetime'], name='idx_events_public_start'),
            models.Index(fields=['category'], name='idx_events_category'),
            models.Index(fields=['status'], name='idx_events_status'),
        ]
        ordering = ['-start_datetime']
    
    def __str__(self):
        return self.name


class TicketType(models.Model):
    """チケット種別モデル"""
    
    TYPE_CHOICES = [
        ('reserved', '座席指定'),
        ('free', '自由席'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types', verbose_name='イベント')
    
    # チケット種別情報
    name = models.CharField('種別名', max_length=100)
    type = models.CharField('タイプ', max_length=20, choices=TYPE_CHOICES)
    price = models.DecimalField('価格', max_digits=10, decimal_places=2)
    
    # 販売管理
    total_quantity = models.IntegerField('総販売枚数')
    sold_quantity = models.IntegerField('販売済枚数', default=0)
    
    # 販売期間
    sale_start = models.DateTimeField('販売開始日時', null=True, blank=True)
    sale_end = models.DateTimeField('販売終了日時', null=True, blank=True)
    
    # タイムスタンプ
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'ticket_types'
        verbose_name = 'チケット種別'
        verbose_name_plural = 'チケット種別'
        indexes = [
            models.Index(fields=['event'], name='idx_ticket_types_event'),
        ]
    
    def __str__(self):
        return f"{self.event.name} - {self.name}"
    
    @property
    def remaining_quantity(self):
        """残り枚数"""
        return self.total_quantity - self.sold_quantity
    
    @property
    def is_sold_out(self):
        """売り切れかどうか"""
        return self.sold_quantity >= self.total_quantity

