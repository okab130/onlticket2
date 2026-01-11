# Phase 0 Research: TicketPro オンラインチケット販売システム MVP

**Date**: 2026-01-11  
**Status**: Completed  
**Plan Reference**: [plan.md](./plan.md)

## Overview

このドキュメントは、TicketPro MVPの実装に必要な技術調査結果をまとめたものです。Django 5.2+、PostgreSQL、Celery + Redisを使用したオンラインチケット販売システムの実装に必要な8つの主要トピックを調査しました。

---

## 1. Django Transaction Control（トランザクション制御）

### 目的
座席の二重販売を防止し、カート仮予約のタイムアウトを実装する。

### Django Transaction Management

#### 基本的な使い方

```python
from django.db import transaction

# デコレータ方式（推奨）
@transaction.atomic
def purchase_ticket(user, seat_id):
    """座席購入処理（原子性保証）"""
    seat = Seat.objects.select_for_update().get(id=seat_id)
    
    if seat.status != 'available':
        raise ValueError("この座席は既に予約されています")
    
    # 座席ステータス更新
    seat.status = 'sold'
    seat.save()
    
    # 注文作成
    order = Order.objects.create(user=user, total_amount=seat.price)
    
    # チケット発行
    ticket = Ticket.objects.create(order=order, seat=seat)
    
    return order

# コンテキストマネージャ方式
def reserve_seat_with_timeout(user, seat_id):
    """座席を仮予約（10分間のタイムアウト付き）"""
    try:
        with transaction.atomic():
            seat = Seat.objects.select_for_update(nowait=True).get(id=seat_id)
            
            if seat.status != 'available':
                return None
            
            seat.status = 'reserved'
            seat.reserved_by = user
            seat.reserved_at = timezone.now()
            seat.save()
            
            return seat
    except DatabaseError:
        # 他のユーザーが既にロックしている
        return None
```

#### 二重販売防止の戦略

**1. 悲観的ロック（Pessimistic Locking）**

```python
from django.db import transaction

@transaction.atomic
def purchase_with_pessimistic_lock(user, seat_id):
    """悲観的ロックで二重販売を防止"""
    # select_for_update() で行ロック（他のトランザクションは待機）
    seat = Seat.objects.select_for_update().get(id=seat_id)
    
    if seat.status != 'available':
        raise ValueError("座席は既に予約されています")
    
    seat.status = 'sold'
    seat.save()
    
    order = Order.objects.create(user=user)
    ticket = Ticket.objects.create(order=order, seat=seat)
    
    return order
```

**2. 楽観的ロック（Optimistic Locking）**

```python
from django.db import models, transaction
from django.db.models import F

class Seat(models.Model):
    version = models.IntegerField(default=0)  # バージョンフィールド
    status = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'seats'

@transaction.atomic
def purchase_with_optimistic_lock(user, seat_id):
    """楽観的ロックで二重販売を防止"""
    seat = Seat.objects.get(id=seat_id)
    original_version = seat.version
    
    if seat.status != 'available':
        raise ValueError("座席は既に予約されています")
    
    # バージョン番号をチェックしながら更新
    updated = Seat.objects.filter(
        id=seat_id,
        version=original_version,
        status='available'
    ).update(
        status='sold',
        version=F('version') + 1
    )
    
    if updated == 0:
        # 他のユーザーが既に更新した
        raise ValueError("座席は既に予約されました。別の座席をお選びください。")
    
    seat.refresh_from_db()
    
    order = Order.objects.create(user=user)
    ticket = Ticket.objects.create(order=order, seat=seat)
    
    return order
```

#### 推奨実装方針

**プロトタイプフェーズ**: 悲観的ロック（`select_for_update()`）を推奨
- 理由: 実装がシンプルで、Djangoの標準機能で完結
- パフォーマンス: プロトタイプの規模では十分

**本番環境**: 楽観的ロック + リトライ機構を検討
- 理由: 高並行性に対応、デッドロック回避
- 実装: バージョンフィールド追加、エラーハンドリング強化

### カート仮予約タイムアウトの実装

#### 方法1: Celery Beatによる定期クリーンアップ（推奨）

```python
# tasks/cleanup_tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.seats.models import Seat

@shared_task
def cleanup_expired_reservations():
    """期限切れの座席仮予約をクリーンアップ（1分ごとに実行）"""
    timeout = timezone.now() - timedelta(minutes=10)
    
    expired_seats = Seat.objects.filter(
        status='reserved',
        reserved_at__lt=timeout
    )
    
    count = expired_seats.update(
        status='available',
        reserved_by=None,
        reserved_at=None
    )
    
    return f"{count} seats released"

# tasks/celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('ticketpro')

app.conf.beat_schedule = {
    'cleanup-expired-reservations': {
        'task': 'tasks.cleanup_tasks.cleanup_expired_reservations',
        'schedule': 60.0,  # 60秒ごとに実行
    },
}
```

#### 方法2: データベーストリガー（PostgreSQL）

```sql
-- PostgreSQL関数
CREATE OR REPLACE FUNCTION cleanup_expired_reservations()
RETURNS void AS $$
BEGIN
    UPDATE seats
    SET status = 'available',
        reserved_by = NULL,
        reserved_at = NULL
    WHERE status = 'reserved'
      AND reserved_at < NOW() - INTERVAL '10 minutes';
END;
$$ LANGUAGE plpgsql;

-- 定期実行（pg_cronまたは外部スケジューラ）
SELECT cron.schedule('cleanup-reservations', '* * * * *', 
    'SELECT cleanup_expired_reservations()');
```

#### 推奨実装方針

**プロトタイプフェーズ**: Celery Beat（方法1）を推奨
- 理由: Djangoコード内で完結、デバッグ容易
- 実装: Celery + Redisのセットアップが必要

---

## 2. QR Code Generation in Django

### 目的
チケットにQRコードを生成し、入場時にスキャンして検証する。

### ライブラリ選定

**推奨**: `qrcode` + `Pillow`

```bash
pip install qrcode[pil]
pip install Pillow
```

**理由**:
- シンプルで軽量
- PIL/Pillowと統合されており、画像処理が容易
- Djangoとの相性が良い

### 実装例

#### QRコード生成サービス

```python
# apps/tickets/services.py
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils.crypto import get_random_string
import hashlib
import hmac
from django.conf import settings

class TicketQRService:
    """チケットQRコード生成サービス"""
    
    @staticmethod
    def generate_ticket_number():
        """一意なチケット番号を生成"""
        return get_random_string(16, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    
    @staticmethod
    def generate_signature(ticket_number, secret_key=None):
        """改ざん防止のための署名を生成"""
        if secret_key is None:
            secret_key = settings.SECRET_KEY
        
        signature = hmac.new(
            secret_key.encode(),
            ticket_number.encode(),
            hashlib.sha256
        ).hexdigest()[:16]  # 最初の16文字を使用
        
        return signature
    
    @staticmethod
    def generate_qr_code(ticket):
        """QRコード画像を生成"""
        # QRコードに含めるデータ
        # フォーマット: TICKET_NUMBER|SIGNATURE|EVENT_ID|SEAT_ID
        signature = TicketQRService.generate_signature(ticket.ticket_number)
        qr_data = f"{ticket.ticket_number}|{signature}|{ticket.order.event.id}"
        
        if ticket.seat:
            qr_data += f"|{ticket.seat.id}"
        
        # QRコード生成
        qr = qrcode.QRCode(
            version=1,  # 1-40、大きいほど多くのデータを含む
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 高エラー訂正
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # PIL Imageに変換
        img = qr.make_image(fill_color="black", back_color="white")
        
        # BytesIOに保存
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return File(buffer, name=f'qr_{ticket.ticket_number}.png')
    
    @staticmethod
    def verify_qr_code(qr_data):
        """QRコードの検証（改ざんチェック）"""
        try:
            parts = qr_data.split('|')
            if len(parts) < 3:
                return False, "無効なQRコードフォーマット"
            
            ticket_number = parts[0]
            signature = parts[1]
            
            # 署名を再計算して比較
            expected_signature = TicketQRService.generate_signature(ticket_number)
            
            if signature != expected_signature:
                return False, "改ざんされたQRコードです"
            
            return True, ticket_number
        except Exception as e:
            return False, f"QRコード検証エラー: {str(e)}"
```

#### モデルへの統合

```python
# apps/tickets/models.py
from django.db import models
from django.utils import timezone
from .services import TicketQRService

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('valid', '有効'),
        ('used', '使用済み'),
        ('cancelled', 'キャンセル済み'),
    ]
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    seat = models.ForeignKey('seats.Seat', on_delete=models.SET_NULL, null=True, blank=True)
    ticket_number = models.CharField(max_length=16, unique=True)
    qr_code = models.ImageField(upload_to='tickets/qr_codes/', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='valid')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # 新規作成時にチケット番号とQRコードを自動生成
        if not self.ticket_number:
            self.ticket_number = TicketQRService.generate_ticket_number()
        
        super().save(*args, **kwargs)
        
        # QRコードが未生成の場合は生成
        if not self.qr_code:
            qr_file = TicketQRService.generate_qr_code(self)
            self.qr_code.save(qr_file.name, qr_file, save=True)
    
    def __str__(self):
        return f"Ticket {self.ticket_number}"
```

### セキュリティ考慮事項

1. **署名による改ざん防止**: HMACを使用してチケット番号に署名
2. **一意性**: チケット番号はランダム生成（16文字）
3. **エラー訂正**: QRコードのエラー訂正レベルを高（H）に設定
4. **HTTPSのみ**: QRコードスキャン時の通信はHTTPS必須

---

## 3. PDF Generation in Django

### 目的
QRコード付き電子チケットPDFを生成する。

### ライブラリ選定比較

| ライブラリ | メリット | デメリット | 推奨度 |
|-----------|---------|-----------|--------|
| **ReportLab** | 軽量、高速、細かい制御可能 | HTML非対応、手動レイアウト | ⭐⭐⭐ |
| **WeasyPrint** | HTML/CSS対応、デザイン容易 | 重い、依存関係多い | ⭐⭐ |
| **xhtml2pdf** | HTML対応、シンプル | CSS対応が不完全 | ⭐ |

**推奨**: **ReportLab**
- 理由: プロトタイプには軽量で十分、チケットレイアウトはシンプル
- 将来的にデザインが複雑になる場合はWeasyPrintに移行検討

### ReportLabによる実装

```bash
pip install reportlab
```

#### チケットPDF生成サービス

```python
# apps/tickets/services.py (続き)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
import os

class TicketPDFService:
    """チケットPDF生成サービス"""
    
    @staticmethod
    def generate_ticket_pdf(ticket):
        """チケットPDFを生成"""
        buffer = BytesIO()
        
        # A4サイズのキャンバス作成
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # タイトル
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 50*mm, "Electronic Ticket")
        
        # イベント情報
        event = ticket.order.event
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50*mm, height - 80*mm, "Event:")
        c.setFont("Helvetica", 14)
        c.drawString(50*mm, height - 90*mm, event.name)
        
        # 開催日時
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50*mm, height - 105*mm, "Date & Time:")
        c.setFont("Helvetica", 10)
        c.drawString(50*mm, height - 112*mm, 
                    event.start_datetime.strftime("%Y年%m月%d日 %H:%M"))
        
        # 会場
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50*mm, height - 125*mm, "Venue:")
        c.setFont("Helvetica", 10)
        c.drawString(50*mm, height - 132*mm, event.venue.name)
        
        # 座席情報
        if ticket.seat:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50*mm, height - 145*mm, "Seat:")
            c.setFont("Helvetica", 10)
            seat_info = f"{ticket.seat.block} - Row {ticket.seat.row} - No. {ticket.seat.number}"
            c.drawString(50*mm, height - 152*mm, seat_info)
        else:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50*mm, height - 145*mm, "Free Seating")
        
        # チケット番号
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50*mm, height - 165*mm, "Ticket Number:")
        c.setFont("Courier", 10)
        c.drawString(50*mm, height - 172*mm, ticket.ticket_number)
        
        # QRコード
        if ticket.qr_code:
            qr_path = ticket.qr_code.path
            if os.path.exists(qr_path):
                qr_image = ImageReader(qr_path)
                # QRコードを中央下部に配置（80mm x 80mm）
                c.drawImage(qr_image, 
                           (width - 80*mm) / 2, 
                           50*mm, 
                           width=80*mm, 
                           height=80*mm)
        
        # 注意事項
        c.setFont("Helvetica", 8)
        c.drawString(50*mm, 30*mm, "※ 入場時にこのQRコードをスキャンしてください")
        c.drawString(50*mm, 25*mm, "※ このチケットは1回のみ有効です")
        c.drawString(50*mm, 20*mm, "※ 第三者への譲渡・転売は禁止されています")
        
        # PDF完成
        c.showPage()
        c.save()
        
        buffer.seek(0)
        return File(buffer, name=f'ticket_{ticket.ticket_number}.pdf')
```

#### 日本語フォント対応（必要な場合）

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

# 日本語フォント登録（IPAフォントなど）
def register_japanese_font():
    """日本語フォントを登録"""
    font_path = os.path.join(settings.BASE_DIR, 'static/fonts/ipaexg.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('IPAexGothic', font_path))
        addMapping('IPAexGothic', 0, 0, 'IPAexGothic')  # normal
        return 'IPAexGothic'
    return 'Helvetica'

# 使用例
c.setFont(register_japanese_font(), 14)
c.drawString(50*mm, height - 90*mm, "イベント名：東京コンサート")
```

### PDFダウンロードビュー

```python
# apps/tickets/views.py
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Ticket
from .services import TicketPDFService

@login_required
def download_ticket_pdf(request, ticket_id):
    """チケットPDFをダウンロード"""
    try:
        ticket = Ticket.objects.get(
            id=ticket_id,
            order__user=request.user,
            status='valid'
        )
    except Ticket.DoesNotExist:
        raise Http404("チケットが見つかりません")
    
    # PDF生成
    pdf_file = TicketPDFService.generate_ticket_pdf(ticket)
    
    # レスポンス
    response = FileResponse(
        pdf_file,
        content_type='application/pdf'
    )
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.ticket_number}.pdf"'
    
    return response
```

---

## 4. Celery + Redis Setup

### 目的
非同期でメール送信、定期的に期限切れカートをクリーンアップする。

### インストール

```bash
pip install celery[redis]
pip install redis
```

### Celery設定

#### プロジェクト構成

```python
# config/settings.py
# Celery設定
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tokyo'

# メール設定（プロトタイプではコンソール出力）
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

#### Celeryアプリケーション初期化

```python
# tasks/celery.py
import os
from celery import Celery

# Django設定モジュールを設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('ticketpro')

# Django設定からCelery設定を読み込む
app.config_from_object('django.conf:settings', namespace='CELERY')

# 全てのDjangoアプリからタスクを自動検出
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

#### Django統合

```python
# config/__init__.py
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### メール送信タスク

```python
# tasks/email_tasks.py
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from apps.tickets.models import Ticket
from apps.tickets.services import TicketPDFService

@shared_task
def send_ticket_email(ticket_id):
    """チケット購入完了メールを送信（PDF添付）"""
    try:
        ticket = Ticket.objects.select_related(
            'order__user',
            'order__event',
            'seat'
        ).get(id=ticket_id)
        
        # メール本文生成
        context = {
            'ticket': ticket,
            'event': ticket.order.event,
            'user': ticket.order.user,
        }
        html_message = render_to_string('emails/ticket_purchase.html', context)
        plain_message = render_to_string('emails/ticket_purchase.txt', context)
        
        # PDF生成
        pdf_file = TicketPDFService.generate_ticket_pdf(ticket)
        
        # メール送信
        email = EmailMessage(
            subject=f'チケット購入完了 - {ticket.order.event.name}',
            body=plain_message,
            from_email='noreply@ticketpro.example.com',
            to=[ticket.order.user.email],
        )
        email.attach(f'ticket_{ticket.ticket_number}.pdf', pdf_file.read(), 'application/pdf')
        email.send()
        
        return f"Email sent to {ticket.order.user.email}"
    
    except Ticket.DoesNotExist:
        return f"Ticket {ticket_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"

@shared_task
def send_bulk_notification(event_id, subject, message):
    """イベント参加者への一斉通知"""
    from apps.tickets.models import Ticket
    
    tickets = Ticket.objects.filter(
        order__event_id=event_id,
        status='valid'
    ).select_related('order__user')
    
    email_list = [ticket.order.user.email for ticket in tickets]
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email='noreply@ticketpro.example.com',
        bcc=email_list,
    )
    email.send()
    
    return f"Sent to {len(email_list)} recipients"
```

### 定期クリーンアップタスク

```python
# tasks/cleanup_tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.seats.models import Seat

@shared_task
def cleanup_expired_reservations():
    """期限切れの座席仮予約をクリーンアップ"""
    timeout = timezone.now() - timedelta(minutes=10)
    
    expired_seats = Seat.objects.filter(
        status='reserved',
        reserved_at__lt=timeout
    )
    
    count = expired_seats.update(
        status='available',
        reserved_by=None,
        reserved_at=None
    )
    
    return f"Released {count} expired reservations"
```

### Celery Beatスケジュール設定

```python
# config/settings.py (追加)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-reservations': {
        'task': 'tasks.cleanup_tasks.cleanup_expired_reservations',
        'schedule': 60.0,  # 60秒ごと
    },
}
```

### Celery起動コマンド

```bash
# Celeryワーカー起動
celery -A tasks worker -l info

# Celery Beat起動（定期タスク用）
celery -A tasks beat -l info

# Windows環境の場合
celery -A tasks worker -l info --pool=solo
```

### タスク呼び出し例

```python
# apps/orders/views.py
from tasks.email_tasks import send_ticket_email

def complete_purchase(request, order_id):
    """購入完了処理"""
    order = Order.objects.get(id=order_id)
    
    # チケット発行
    for item in order.items.all():
        ticket = Ticket.objects.create(order=order, seat=item.seat)
        
        # 非同期でメール送信
        send_ticket_email.delay(ticket.id)
    
    return redirect('purchase_complete', order_id=order.id)
```

---

## 5. Django Security Best Practices

### 目的
CSRF、SQLインジェクション、XSS、Brute force攻撃から保護する。

### Django標準のセキュリティ機能

#### 1. CSRF対策（Django標準）

```python
# config/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF保護
    # ... other middleware
]

# テンプレート
# {% csrf_token %} を全てのフォームに含める
```

```html
<!-- templates/orders/checkout.html -->
<form method="post" action="{% url 'checkout' %}">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">購入確定</button>
</form>
```

#### 2. SQLインジェクション対策（Django ORM）

```python
# ❌ 危険: 生のSQL（使用禁止）
query = f"SELECT * FROM users WHERE username = '{username}'"

# ✅ 安全: Django ORM（推奨）
user = User.objects.get(username=username)

# ✅ 安全: パラメータ化されたクエリ（必要な場合のみ）
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE username = %s", [username])
```

#### 3. XSS対策（テンプレート自動エスケープ）

```html
<!-- Django Templatesは自動的にエスケープ -->
<p>{{ user_input }}</p>  <!-- 自動エスケープ -->

<!-- 意図的にエスケープを無効化する場合（注意） -->
<p>{{ html_content|safe }}</p>  <!-- 信頼できるHTMLのみ -->

<!-- Markdownなどを使う場合 -->
{% load markdown %}
<div>{{ content|markdown|safe }}</div>  <!-- サニタイズ後にsafe -->
```

#### 4. Brute Force攻撃対策

**方法1: django-axes（推奨）**

```bash
pip install django-axes
```

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'axes',
]

MIDDLEWARE = [
    # AxesMiddlewareはAuthenticationMiddlewareの後に配置
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',  # Axesバックエンドを先に
    'django.contrib.auth.backends.ModelBackend',
]

# Axes設定
AXES_FAILURE_LIMIT = 5  # 5回失敗でロック
AXES_COOLOFF_TIME = 1  # 1時間後に自動解除
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
```

**方法2: カスタム実装（シンプル版）**

```python
# apps/members/models.py
from django.contrib.auth.models import User
from django.db import models

class LoginAttempt(models.Model):
    """ログイン試行記録"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ip_address = models.GenericIPAddressField()
    attempted_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

# apps/members/views.py
from django.contrib.auth import authenticate, login
from django.utils import timezone
from datetime import timedelta
from .models import LoginAttempt

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        ip = get_client_ip(request)
        
        # 過去10分間の失敗回数をチェック
        recent_failures = LoginAttempt.objects.filter(
            user__username=username,
            ip_address=ip,
            success=False,
            attempted_at__gte=timezone.now() - timedelta(minutes=10)
        ).count()
        
        if recent_failures >= 5:
            return render(request, 'members/login.html', {
                'error': 'アカウントが一時的にロックされています。10分後に再試行してください。'
            })
        
        user = authenticate(username=username, password=password)
        
        if user:
            LoginAttempt.objects.create(user=user, ip_address=ip, success=True)
            login(request, user)
            return redirect('home')
        else:
            LoginAttempt.objects.create(
                user=User.objects.filter(username=username).first(),
                ip_address=ip,
                success=False
            )
            return render(request, 'members/login.html', {
                'error': 'ユーザー名またはパスワードが正しくありません。'
            })
    
    return render(request, 'members/login.html')

def get_client_ip(request):
    """クライアントIPアドレスを取得"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

### セキュリティ設定のチェックリスト

```python
# config/settings.py

# HTTPS強制（本番環境）
SECURE_SSL_REDIRECT = True  # プロトタイプではFalse
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Cookie設定
SESSION_COOKIE_SECURE = True  # HTTPS必須（プロトタイプではFalse）
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# パスワード検証
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# デバッグ設定
DEBUG = False  # 本番環境では必ずFalse（プロトタイプではTrue）
ALLOWED_HOSTS = ['yourdomain.com']  # 本番環境では明示的に指定

# SECRET_KEYは環境変数から読み込む
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')
```

---

## 6. N+1 Problem Prevention

### 目的
データベースクエリを最適化し、N+1問題を回避する。

### N+1問題とは

```python
# ❌ N+1問題の例
events = Event.objects.all()
for event in events:
    print(event.venue.name)  # 各eventごとにvenueを取得するクエリが発行される
    # クエリ数 = 1 (events取得) + N (各eventのvenue取得) = N+1
```

### select_related（1対1、多対1リレーション）

```python
# ✅ select_relatedで最適化（JOIN使用）
events = Event.objects.select_related('venue').all()
for event in events:
    print(event.venue.name)  # 追加クエリなし
    # クエリ数 = 1 (JOINしたクエリ1回のみ)

# 複数のリレーションを一度に取得
tickets = Ticket.objects.select_related(
    'order',
    'order__user',
    'seat'
).all()

for ticket in tickets:
    print(ticket.order.user.username)  # 追加クエリなし
    print(ticket.seat.number)  # 追加クエリなし
```

### prefetch_related（多対多、逆参照）

```python
# ❌ N+1問題の例（逆参照）
events = Event.objects.all()
for event in events:
    print(event.tickets.count())  # 各eventごとにticketsを取得するクエリ

# ✅ prefetch_relatedで最適化
events = Event.objects.prefetch_related('tickets').all()
for event in events:
    print(event.tickets.count())  # 追加クエリなし
    # クエリ数 = 2 (events取得 + 全ticketsを一括取得)

# 複数のprefetch
events = Event.objects.prefetch_related(
    'tickets',
    'tickets__seat',
    'tickettypes'
).all()
```

### Prefetchオブジェクトによる高度な最適化

```python
from django.db.models import Prefetch

# 有効なチケットのみをprefetch
events = Event.objects.prefetch_related(
    Prefetch(
        'tickets',
        queryset=Ticket.objects.filter(status='valid').select_related('seat')
    )
).all()

for event in events:
    for ticket in event.tickets.all():
        print(ticket.seat.number)  # 追加クエリなし
```

### 集計クエリの最適化

```python
from django.db.models import Count, Sum, Avg

# ❌ 非効率: 各イベントで個別に集計
events = Event.objects.all()
for event in events:
    sold_count = event.tickets.filter(status='sold').count()
    # 各イベントごとにクエリ発行

# ✅ 効率的: annotateで一括集計
events = Event.objects.annotate(
    sold_count=Count('tickets', filter=Q(tickets__status='sold')),
    total_revenue=Sum('tickets__order__total_amount')
).all()

for event in events:
    print(event.sold_count)  # 追加クエリなし
    print(event.total_revenue)  # 追加クエリなし
```

### Django Debug Toolbarでクエリ確認

```bash
pip install django-debug-toolbar
```

```python
# config/settings.py (開発環境のみ)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

# config/urls.py (開発環境のみ)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
```

### 実装ガイドライン

```python
# apps/events/views.py
from django.views.generic import ListView
from .models import Event

class EventListView(ListView):
    """イベント一覧（最適化済み）"""
    model = Event
    template_name = 'events/event_list.html'
    
    def get_queryset(self):
        return Event.objects.select_related(
            'venue',
            'organizer'
        ).prefetch_related(
            'tickettypes'
        ).filter(
            is_public=True
        ).order_by('-start_datetime')
```

---

## 7. Responsive UI with Bootstrap + Alpine.js

### 目的
レスポンシブなUI（PC、タブレット、スマホ対応）を構築する。

### Bootstrap 5導入

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}TicketPro{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/custom.css' %}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- ナビゲーションバー -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}">TicketPro</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{% url 'event_list' %}">イベント</a></li>
                    {% if user.is_authenticated %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'mypage' %}">マイページ</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'logout' %}">ログアウト</a></li>
                    {% else %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'login' %}">ログイン</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'register' %}">会員登録</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- メインコンテンツ -->
    <main class="container my-4">
        {% block content %}{% endblock %}
    </main>
    
    <!-- フッター -->
    <footer class="bg-dark text-white text-center py-3 mt-5">
        <p>&copy; 2026 TicketPro. All rights reserved.</p>
    </footer>
    
    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Alpine.js導入と座席選択UI

```html
<!-- templates/seats/seat_selection.html -->
{% extends 'base.html' %}

{% block extra_css %}
<style>
    .seat {
        width: 40px;
        height: 40px;
        margin: 5px;
        border: 2px solid #ccc;
        border-radius: 5px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }
    .seat.available { background-color: #28a745; color: white; }
    .seat.reserved { background-color: #ffc107; color: black; cursor: not-allowed; }
    .seat.sold { background-color: #dc3545; color: white; cursor: not-allowed; }
    .seat.selected { background-color: #007bff; color: white; border: 3px solid #0056b3; }
</style>
{% endblock %}

{% block content %}
<h2>座席選択 - {{ event.name }}</h2>

<div x-data="seatSelection()" x-init="init()">
    <!-- 選択済み座席 -->
    <div class="alert alert-info">
        <strong>選択中の座席:</strong>
        <span x-text="selectedSeats.length"></span> 席
        <template x-for="seat in selectedSeats" :key="seat.id">
            <span class="badge bg-primary mx-1" x-text="seat.label"></span>
        </template>
    </div>
    
    <!-- 座席表 -->
    <div class="text-center">
        <div class="bg-secondary text-white p-2 mb-4">ステージ</div>
        
        <template x-for="block in seatMap" :key="block.name">
            <div class="mb-4">
                <h5 x-text="block.name"></h5>
                <template x-for="row in block.rows" :key="row.label">
                    <div class="d-flex justify-content-center mb-2">
                        <span class="me-2" x-text="row.label"></span>
                        <template x-for="seat in row.seats" :key="seat.id">
                            <button 
                                class="seat"
                                :class="getSeatClass(seat)"
                                @click="toggleSeat(seat)"
                                :disabled="seat.status !== 'available' && !isSelected(seat)"
                                x-text="seat.number">
                            </button>
                        </template>
                    </div>
                </template>
            </div>
        </template>
    </div>
    
    <!-- カートに追加ボタン -->
    <div class="text-center mt-4">
        <button 
            class="btn btn-primary btn-lg"
            @click="addToCart()"
            :disabled="selectedSeats.length === 0">
            カートに追加 (<span x-text="selectedSeats.length"></span> 席)
        </button>
    </div>
</div>

<!-- Alpine.js CDN -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

<script>
function seatSelection() {
    return {
        seatMap: [],
        selectedSeats: [],
        
        init() {
            // 座席データを取得（APIまたはDjangoコンテキスト）
            this.seatMap = {{ seat_map_json|safe }};
        },
        
        getSeatClass(seat) {
            if (this.isSelected(seat)) return 'selected';
            return seat.status;
        },
        
        isSelected(seat) {
            return this.selectedSeats.some(s => s.id === seat.id);
        },
        
        toggleSeat(seat) {
            if (seat.status !== 'available') return;
            
            const index = this.selectedSeats.findIndex(s => s.id === seat.id);
            if (index > -1) {
                this.selectedSeats.splice(index, 1);
            } else {
                this.selectedSeats.push({
                    id: seat.id,
                    label: `${seat.block}-${seat.row}-${seat.number}`
                });
            }
        },
        
        addToCart() {
            if (this.selectedSeats.length === 0) return;
            
            const seatIds = this.selectedSeats.map(s => s.id);
            
            // カートに追加（Ajaxリクエスト）
            fetch('{% url "add_to_cart" %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({ seat_ids: seatIds })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '{% url "cart" %}';
                } else {
                    alert(data.error);
                }
            });
        }
    }
}
</script>
{% endblock %}
```

### レスポンシブデザインのポイント

```css
/* static/css/custom.css */

/* モバイルファースト */
.seat {
    width: 30px;
    height: 30px;
    font-size: 10px;
}

/* タブレット以上 */
@media (min-width: 768px) {
    .seat {
        width: 40px;
        height: 40px;
        font-size: 12px;
    }
}

/* PC */
@media (min-width: 1024px) {
    .seat {
        width: 50px;
        height: 50px;
        font-size: 14px;
    }
}
```

---

## 8. Django Testing Best Practices

### 目的
主要フローの統合テストと単体テストを実装する。

### pytest-djangoセットアップ

```bash
pip install pytest pytest-django factory-boy
```

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
addopts = --reuse-db --nomigrations
```

```python
# tests/conftest.py
import pytest
from django.contrib.auth.models import User
from apps.events.models import Event, Venue
from apps.seats.models import Seat

@pytest.fixture
def user(db):
    """テストユーザー"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def venue(db):
    """テスト会場"""
    return Venue.objects.create(
        name='Test Venue',
        address='Tokyo',
        capacity=100
    )

@pytest.fixture
def event(db, venue):
    """テストイベント"""
    from django.utils import timezone
    from datetime import timedelta
    
    return Event.objects.create(
        name='Test Concert',
        venue=venue,
        start_datetime=timezone.now() + timedelta(days=7),
        is_public=True
    )

@pytest.fixture
def available_seat(db, venue):
    """空席"""
    return Seat.objects.create(
        venue=venue,
        block='A',
        row='1',
        number='1',
        status='available'
    )
```

### Factory Boyによるテストデータ生成

```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from apps.events.models import Event, Venue
from apps.seats.models import Seat

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class VenueFactory(DjangoModelFactory):
    class Meta:
        model = Venue
    
    name = factory.Sequence(lambda n: f'Venue {n}')
    address = 'Tokyo'
    capacity = 100

class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event
    
    name = factory.Sequence(lambda n: f'Event {n}')
    venue = factory.SubFactory(VenueFactory)
    start_datetime = factory.Faker('future_datetime', tzinfo=timezone.utc)
    is_public = True

class SeatFactory(DjangoModelFactory):
    class Meta:
        model = Seat
    
    venue = factory.SubFactory(VenueFactory)
    block = 'A'
    row = factory.Sequence(lambda n: str(n))
    number = factory.Sequence(lambda n: str(n))
    status = 'available'
```

### 統合テスト例

```python
# tests/integration/test_purchase_flow.py
import pytest
from django.urls import reverse
from apps.tickets.models import Ticket
from apps.orders.models import Order

@pytest.mark.django_db
class TestPurchaseFlow:
    """チケット購入フローの統合テスト"""
    
    def test_complete_purchase_flow(self, client, user, event, available_seat):
        """座席選択からチケット購入完了までの完全フロー"""
        # ログイン
        client.login(username='testuser', password='testpass123')
        
        # イベント詳細ページ表示
        response = client.get(reverse('event_detail', args=[event.id]))
        assert response.status_code == 200
        
        # 座席選択ページ表示
        response = client.get(reverse('seat_selection', args=[event.id]))
        assert response.status_code == 200
        
        # カートに座席追加
        response = client.post(
            reverse('add_to_cart'),
            data={'seat_ids': [available_seat.id]},
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # カート確認
        response = client.get(reverse('cart'))
        assert response.status_code == 200
        
        # 購入確定
        response = client.post(reverse('checkout'))
        assert response.status_code == 302  # リダイレクト
        
        # 注文が作成されたことを確認
        order = Order.objects.filter(user=user).first()
        assert order is not None
        
        # チケットが作成されたことを確認
        ticket = Ticket.objects.filter(order=order).first()
        assert ticket is not None
        assert ticket.seat == available_seat
        
        # 座席ステータスが更新されたことを確認
        available_seat.refresh_from_db()
        assert available_seat.status == 'sold'
    
    def test_prevent_double_purchase(self, client, user, event, available_seat):
        """二重購入の防止テスト"""
        from django.contrib.auth.models import User
        
        # 2人のユーザーを作成
        user1 = User.objects.create_user('user1', password='pass')
        user2 = User.objects.create_user('user2', password='pass')
        
        # user1がログインして購入
        client.login(username='user1', password='pass')
        client.post(
            reverse('add_to_cart'),
            data={'seat_ids': [available_seat.id]},
            content_type='application/json'
        )
        client.post(reverse('checkout'))
        
        # user2がログインして同じ座席を購入しようとする
        client.logout()
        client.login(username='user2', password='pass')
        response = client.post(
            reverse('add_to_cart'),
            data={'seat_ids': [available_seat.id]},
            content_type='application/json'
        )
        
        # エラーメッセージを確認
        data = response.json()
        assert not data['success']
        assert '既に予約されています' in data['error']
```

### 単体テスト例

```python
# tests/unit/test_models.py
import pytest
from apps.tickets.services import TicketQRService

@pytest.mark.django_db
class TestTicketModel:
    """Ticketモデルの単体テスト"""
    
    def test_ticket_number_generation(self, user, event, available_seat):
        """チケット番号が自動生成されることを確認"""
        from apps.orders.models import Order
        from apps.tickets.models import Ticket
        
        order = Order.objects.create(user=user)
        ticket = Ticket.objects.create(order=order, seat=available_seat)
        
        assert ticket.ticket_number is not None
        assert len(ticket.ticket_number) == 16
    
    def test_qr_code_generation(self, user, event, available_seat):
        """QRコードが自動生成されることを確認"""
        from apps.orders.models import Order
        from apps.tickets.models import Ticket
        
        order = Order.objects.create(user=user)
        ticket = Ticket.objects.create(order=order, seat=available_seat)
        
        assert ticket.qr_code is not None
        assert ticket.qr_code.name.startswith('tickets/qr_codes/')
    
    def test_qr_code_verification(self):
        """QRコード検証の単体テスト"""
        ticket_number = 'TEST1234567890AB'
        signature = TicketQRService.generate_signature(ticket_number)
        qr_data = f"{ticket_number}|{signature}|1"
        
        valid, result = TicketQRService.verify_qr_code(qr_data)
        assert valid
        assert result == ticket_number
    
    def test_qr_code_verification_tampered(self):
        """改ざんされたQRコードの検証"""
        qr_data = "FAKE1234567890AB|FAKESIGNATURE|1"
        
        valid, error = TicketQRService.verify_qr_code(qr_data)
        assert not valid
        assert '改ざんされた' in error
```

### テスト実行

```bash
# すべてのテストを実行
pytest

# 特定のテストを実行
pytest tests/integration/test_purchase_flow.py

# カバレッジ付きで実行
pytest --cov=apps --cov-report=html

# 並列実行（高速化）
pytest -n auto
```

---

## まとめと推奨実装順序

### Phase 0 完了チェックリスト

- ✅ Django Transaction Control（トランザクション制御）
- ✅ QR Code Generation（QRコード生成）
- ✅ PDF Generation（PDF生成）
- ✅ Celery + Redis Setup（非同期処理）
- ✅ Django Security Best Practices（セキュリティ）
- ✅ N+1 Problem Prevention（クエリ最適化）
- ✅ Responsive UI with Bootstrap + Alpine.js（レスポンシブUI）
- ✅ Django Testing Best Practices（テスト）

### 推奨実装順序

1. **Phase 1へ進む**: データモデル設計とUI mockup作成
   - `data-model.md` - ER図、モデル定義
   - `ui-mockups/` - 画面モック（NON-NEGOTIABLE）
   - `quickstart.md` - 開発環境セットアップ

2. **Phase 2へ進む**: `/speckit.tasks`でタスク分解
   - Setup → Foundational → User Stories (P1→P2→P3) → Polish

### 技術選定サマリー

| カテゴリ | 選定技術 | 理由 |
|---------|---------|------|
| トランザクション | `select_for_update()` | シンプル、Django標準 |
| QRコード | qrcode + Pillow | 軽量、高機能 |
| PDF生成 | ReportLab | 軽量、高速 |
| 非同期処理 | Celery + Redis | 実績豊富、Django標準的 |
| セキュリティ | Django標準 + django-axes | 実装容易、十分な機能 |
| クエリ最適化 | select_related, prefetch_related | Django標準、強力 |
| フロントエンド | Bootstrap 5 + Alpine.js | 軽量、学習コスト低 |
| テスト | pytest-django + Factory Boy | 高機能、メンテナンス容易 |

---

**Phase 0 完了日**: 2026-01-11  
**次のステップ**: Phase 1（Design & Mockups）
