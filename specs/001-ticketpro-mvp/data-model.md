# Data Model Design: TicketPro オンラインチケット販売システム MVP

**Date**: 2026-01-11  
**Status**: Completed  
**Plan Reference**: [plan.md](./plan.md)

## Overview

このドキュメントは、TicketPro MVPのデータモデル設計をまとめたものです。11の主要エンティティとその関係性、フィールド定義、インデックス設計、マイグレーション計画を記載しています。

---

## Entity Relationship Diagram (ER図)

```
┌─────────────────┐
│   Organizer     │
│  (主催者)       │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐        ┌─────────────────┐
│     Event       │        │     Venue       │
│   (イベント)     │◄──────┤    (会場)       │
└────────┬────────┘   N:1  └────────┬────────┘
         │                           │
         │ 1                         │ 1
         │                           │
         │ N                         │ N
┌────────▼────────┐        ┌────────▼────────┐
│   TicketType    │        │      Seat       │
│ (チケット種別)   │        │     (座席)      │
└────────┬────────┘        └────────┬────────┘
         │                           │
         │                           │
         └───────────┬───────────────┘
                     │
                     │
         ┌───────────▼───────────┐
         │       Order           │
         │      (注文)           │
         │                       │
         │  User (購入者) N:1 ───┼─────┐
         └───────────┬───────────┘     │
                     │                 │
                     │ 1               │ N
                     │                 │
                     │ N          ┌────▼──────┐
         ┌───────────▼───────────┐│   User    │
         │      Ticket           ││  (会員)   │
         │    (チケット)          │└───────────┘
         └───────────┬───────────┘
                     │
         ┌───────────┼───────────┐
         │ 1         │           │ 1
         │           │           │
         │ 1         │ 1         │ N
┌────────▼────────┐ │  ┌────────▼────────┐
│    Payment      │ │  │     Entry       │
│    (決済)       │ │  │   (入場記録)     │
└─────────────────┘ │  └─────────────────┘
                    │
                    │ 1
                    │
                    │ 1
         ┌──────────▼───────────┐
         │   Cancellation       │
         │  (キャンセル)         │
         └──────────────────────┘
```

---

## Models Definition

### 1. User (会員・購入者)

Django標準のUserモデルを拡張します。

```python
# apps/members/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """会員モデル（Django標準Userを拡張）"""
    
    # 追加フィールド
    phone_number = models.CharField('電話番号', max_length=20, blank=True)
    birth_date = models.DateField('生年月日', null=True, blank=True)
    
    # ログイン試行管理（Brute force対策）
    failed_login_attempts = models.IntegerField('ログイン失敗回数', default=0)
    last_failed_login = models.DateTimeField('最終ログイン失敗日時', null=True, blank=True)
    account_locked_until = models.DateTimeField('アカウントロック期限', null=True, blank=True)
    
    # タイムスタンプ
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '会員'
        verbose_name_plural = '会員'
        indexes = [
            models.Index(fields=['email'], name='idx_users_email'),
            models.Index(fields=['created_at'], name='idx_users_created_at'),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
```

**主要フィールド**:
- `username`: ユーザー名（Django標準、ユニーク）
- `email`: メールアドレス（Django標準、ログインに使用）
- `password`: パスワード（Django標準、ハッシュ化）
- `phone_number`: 電話番号
- `failed_login_attempts`: ログイン失敗回数（5回でロック）

---

### 2. Organizer (主催者)

```python
# apps/organizers/models.py
from django.db import models
from django.contrib.auth.models import User

class Organizer(models.Model):
    """主催者モデル"""
    
    ROLE_CHOICES = [
        ('admin', '管理者'),
        ('staff', 'スタッフ'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='ユーザー')
    organization_name = models.CharField('組織名', max_length=200)
    role = models.CharField('権限', max_length=20, choices=ROLE_CHOICES, default='staff')
    
    # 連絡先
    contact_email = models.EmailField('連絡先メール')
    contact_phone = models.CharField('連絡先電話', max_length=20)
    
    # タイムスタンプ
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'organizers'
        verbose_name = '主催者'
        verbose_name_plural = '主催者'
    
    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"
```

---

### 3. Venue (会場)

```python
# apps/events/models.py
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
```

---

### 4. Seat (座席)

```python
# apps/seats/models.py
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
    block = models.CharField('ブロック', max_length=50)  # 例: "1階", "2階", "アリーナ"
    row = models.CharField('列', max_length=10)  # 例: "A", "1"
    number = models.CharField('番号', max_length=10)  # 例: "1", "10"
    seat_type = models.CharField('座席種別', max_length=1, choices=SEAT_TYPE_CHOICES)
    
    # ステータス
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='available')
    
    # 仮予約情報
    reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='reserved_seats', verbose_name='仮予約者')
    reserved_at = models.DateTimeField('仮予約日時', null=True, blank=True)
    
    # 楽観的ロック用（オプション）
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
```

---

### 5. Event (イベント)

```python
# apps/events/models.py (続き)
from django.db import models
from apps.organizers.models import Organizer

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
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='events', verbose_name='主催者')
    
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
```

---

### 6. TicketType (チケット種別)

```python
# apps/events/models.py (続き)
class TicketType(models.Model):
    """チケット種別モデル"""
    
    TYPE_CHOICES = [
        ('reserved', '座席指定'),
        ('free', '自由席'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types', verbose_name='イベント')
    
    # チケット種別情報
    name = models.CharField('種別名', max_length=100)  # 例: "S席", "A席", "自由席"
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
```

---

### 7. Order (注文)

```python
# apps/orders/models.py
from django.db import models
from apps.members.models import User
from apps.events.models import Event

class Order(models.Model):
    """注文モデル"""
    
    STATUS_CHOICES = [
        ('pending', '決済待ち'),
        ('paid', '決済完了'),
        ('failed', '決済失敗'),
        ('cancelled', 'キャンセル済'),
    ]
    
    # 注文情報
    order_number = models.CharField('注文番号', max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='購入者')
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='orders', verbose_name='イベント')
    
    # 金額
    total_amount = models.DecimalField('合計金額', max_digits=10, decimal_places=2)
    
    # ステータス
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # タイムスタンプ
    created_at = models.DateTimeField('注文日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = '注文'
        verbose_name_plural = '注文'
        indexes = [
            models.Index(fields=['user', 'created_at'], name='idx_orders_user_created'),
            models.Index(fields=['status'], name='idx_orders_status'),
            models.Index(fields=['order_number'], name='idx_orders_order_number'),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def generate_order_number(self):
        """注文番号を生成"""
        import uuid
        return f"ORD{uuid.uuid4().hex[:16].upper()}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
```

---

### 8. Ticket (チケット)

```python
# apps/tickets/models.py
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
    
    # 関連
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets', verbose_name='注文')
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='tickets', verbose_name='座席')
    
    # チケット情報
    ticket_number = models.CharField('チケット番号', max_length=16, unique=True)
    qr_code = models.ImageField('QRコード', upload_to='tickets/qr_codes/', blank=True)
    
    # ステータス
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='valid')
    
    # タイムスタンプ
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
    
    def save(self, *args, **kwargs):
        # チケット番号とQRコードの自動生成はsignalで処理
        super().save(*args, **kwargs)
```

---

### 9. Payment (決済)

```python
# apps/orders/models.py (続き)
class Payment(models.Model):
    """決済モデル"""
    
    METHOD_CHOICES = [
        ('credit_card', 'クレジットカード'),
        ('convenience', 'コンビニ決済'),
        ('bank_transfer', '銀行振込'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '決済待ち'),
        ('completed', '決済完了'),
        ('failed', '決済失敗'),
        ('refunded', '返金済み'),
    ]
    
    # 関連
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name='注文')
    
    # 決済情報
    method = models.CharField('決済方法', max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField('決済金額', max_digits=10, decimal_places=2)
    
    # ステータス
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 決済API連携情報（プロトタイプでは不要）
    transaction_id = models.CharField('トランザクションID', max_length=100, blank=True)
    
    # タイムスタンプ
    created_at = models.DateTimeField('決済日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = '決済'
        verbose_name_plural = '決済'
        indexes = [
            models.Index(fields=['status'], name='idx_payments_status'),
        ]
    
    def __str__(self):
        return f"Payment for {self.order.order_number}"
```

---

### 10. Entry (入場記録)

```python
# apps/entries/models.py
from django.db import models
from apps.tickets.models import Ticket
from apps.members.models import User

class Entry(models.Model):
    """入場記録モデル"""
    
    # 関連
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='entries', verbose_name='チケット')
    
    # 入場情報
    gate = models.CharField('ゲート', max_length=50)
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                    related_name='scanned_entries', verbose_name='スキャンスタッフ')
    
    # タイムスタンプ
    entered_at = models.DateTimeField('入場日時', auto_now_add=True)
    
    class Meta:
        db_table = 'entries'
        verbose_name = '入場記録'
        verbose_name_plural = '入場記録'
        indexes = [
            models.Index(fields=['ticket'], name='idx_entries_ticket'),
            models.Index(fields=['entered_at'], name='idx_entries_entered_at'),
        ]
        ordering = ['-entered_at']
    
    def __str__(self):
        return f"Entry for {self.ticket.ticket_number} at {self.entered_at}"
```

---

### 11. Cancellation (キャンセル)

```python
# apps/orders/models.py (続き)
class Cancellation(models.Model):
    """キャンセルモデル"""
    
    STATUS_CHOICES = [
        ('pending', '申請中'),
        ('approved', '承認済み'),
        ('rejected', '却下'),
    ]
    
    # 関連
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='cancellation', verbose_name='注文')
    
    # キャンセル情報
    reason = models.TextField('キャンセル理由')
    refund_amount = models.DecimalField('返金額', max_digits=10, decimal_places=2)
    
    # ステータス
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # タイムスタンプ
    requested_at = models.DateTimeField('申請日時', auto_now_add=True)
    processed_at = models.DateTimeField('処理日時', null=True, blank=True)
    
    class Meta:
        db_table = 'cancellations'
        verbose_name = 'キャンセル'
        verbose_name_plural = 'キャンセル'
        indexes = [
            models.Index(fields=['status'], name='idx_cancellations_status'),
        ]
    
    def __str__(self):
        return f"Cancellation for {self.order.order_number}"
```

---

## Index Strategy

### パフォーマンス最適化のためのインデックス

| テーブル | インデックス | 目的 |
|---------|------------|------|
| users | email | ログイン検索 |
| users | created_at | 会員登録日順ソート |
| events | (is_public, start_datetime) | 公開イベント検索 |
| events | category | カテゴリ検索 |
| seats | (venue, status) | 会場別空席検索 |
| seats | (status, reserved_at) | カートタイムアウトクリーンアップ |
| orders | (user, created_at) | 購入履歴表示 |
| orders | order_number | 注文番号検索 |
| tickets | ticket_number | QRコードスキャン |
| entries | ticket | 入場履歴検索 |

---

## Migration Plan

### マイグレーション順序

```bash
# 1. 基本モデル（依存関係なし）
python manage.py makemigrations members    # User
python manage.py makemigrations organizers # Organizer
python manage.py makemigrations events     # Venue

# 2. 依存モデル（Venue依存）
python manage.py makemigrations events     # Event (Venue, Organizer依存)
python manage.py makemigrations seats      # Seat (Venue依存)

# 3. チケット種別（Event依存）
python manage.py makemigrations events     # TicketType (Event依存)

# 4. 注文関連（Event, User依存）
python manage.py makemigrations orders     # Order, Payment, Cancellation

# 5. チケット関連（Order, Seat依存）
python manage.py makemigrations tickets    # Ticket

# 6. 入場記録（Ticket依存）
python manage.py makemigrations entries    # Entry

# すべてのマイグレーションを実行
python manage.py migrate
```

---

## Data Integrity Constraints

### トランザクション制御が必要な処理

1. **座席購入処理**: `select_for_update()` で座席をロック
2. **カート追加処理**: `select_for_update()` で座席ステータス確認
3. **キャンセル処理**: 注文・チケット・座席の一括更新
4. **入場処理**: チケットステータス更新と入場記録作成

### カスケード削除ルール

- **Venue削除**: Eventは削除不可（PROTECT）
- **Event削除**: Orderは削除不可（PROTECT）、TicketTypeは削除
- **Order削除**: Ticket, Payment, Cancellationは連鎖削除
- **User削除**: Order, Ticket, Entryは連鎖削除

---

## Summary

- **11のエンティティ**: User, Organizer, Venue, Seat, Event, TicketType, Order, Ticket, Payment, Entry, Cancellation
- **主要リレーション**: Event-Venue (N:1), Event-TicketType (1:N), Order-Ticket (1:N), Ticket-Seat (N:1)
- **インデックス**: 検索頻度の高いフィールドに最適化
- **データ整合性**: トランザクション制御とカスケード削除ルール

**Next**: UI Mockups作成
