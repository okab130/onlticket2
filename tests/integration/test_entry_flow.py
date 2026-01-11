"""
入場管理フロー統合テスト
T131: QRスキャン→検証→入場記録→重複入場エラー
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.events.models import Venue, Event
from apps.seats.models import Seat
from apps.tickets.models import Ticket
from apps.orders.models import Order, Payment
from apps.entries.models import Entry
from apps.organizers.models import Organizer
from apps.tickets.services.ticket_service import TicketQRService

User = get_user_model()


@pytest.mark.django_db
class TestEntryFlow(TestCase):
    """入場管理フロー統合テスト"""
    
    def setUp(self):
        """テストデータのセットアップ"""
        # スタッフユーザー作成
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # 購入者作成
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123'
        )
        
        # 主催者作成
        self.organizer_user = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='testpass123'
        )
        self.organizer = Organizer.objects.create(
            user=self.organizer_user,
            organization_name='テスト主催者',
            role='admin'
        )
        
        # 会場作成
        self.venue = Venue.objects.create(
            name='テスト会場',
            address='東京都渋谷区',
            capacity=100
        )
        
        # 座席作成
        self.seat = Seat.objects.create(
            venue=self.venue,
            block='A',
            row='1',
            number='1',
            seat_type='reserved',
            status='available'
        )
        
        # イベント作成（現在時刻から1時間後に開始）
        now = timezone.now()
        self.event = Event.objects.create(
            name='テストイベント',
            description='テスト用イベント',
            category='concert',
            venue=self.venue,
            organizer=self.organizer,
            start_datetime=now + timedelta(hours=1),
            end_datetime=now + timedelta(hours=3),
            is_public=True
        )
        
        # 注文作成
        self.order = Order.objects.create(
            order_number='TEST-ORDER-001',
            user=self.customer,
            event=self.event,
            total_amount=5000,
            status='completed'
        )
        
        # 決済作成
        self.payment = Payment.objects.create(
            order=self.order,
            method='credit_card',
            amount=5000,
            status='completed'
        )
        
        # チケット作成
        qr_service = TicketQRService()
        ticket_number = qr_service.generate_ticket_number()
        qr_code = qr_service.generate_qr_code(ticket_number)
        
        self.ticket = Ticket.objects.create(
            order=self.order,
            seat=self.seat,
            ticket_number=ticket_number,
            qr_code=qr_code,
            status='valid'
        )
        
        # 座席を予約済みに更新
        self.seat.status = 'sold'
        self.seat.reserved_by = self.customer
        self.seat.save()
        
        self.client = Client()
    
    def test_successful_entry_flow(self):
        """正常な入場フロー"""
        # スタッフとしてログイン
        self.client.login(username='staff_user', password='testpass123')
        
        # QRスキャン画面にアクセス
        response = self.client.get(reverse('entries:qr_scan'))
        self.assertEqual(response.status_code, 200)
        
        # チケット検証API呼び出し
        response = self.client.post(reverse('entries:verify_ticket'), {
            'ticket_number': self.ticket.ticket_number,
            'gate': 'メインゲート'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 検証成功
        self.assertTrue(data['success'])
        self.assertIn('入場を許可', data['message'])
        self.assertEqual(data['ticket']['ticket_number'], self.ticket.ticket_number)
        
        # 入場記録が作成されたことを確認
        entry = Entry.objects.filter(ticket=self.ticket).first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.gate, 'メインゲート')
        self.assertEqual(entry.scanned_by, self.staff_user)
        
        # チケットステータスが更新されたことを確認
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'used')
    
    def test_duplicate_entry_prevention(self):
        """重複入場防止テスト"""
        # スタッフとしてログイン
        self.client.login(username='staff_user', password='testpass123')
        
        # 1回目の入場（成功）
        response = self.client.post(reverse('entries:verify_ticket'), {
            'ticket_number': self.ticket.ticket_number,
            'gate': 'メインゲート'
        })
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # 2回目の入場（失敗）
        response = self.client.post(reverse('entries:verify_ticket'), {
            'ticket_number': self.ticket.ticket_number,
            'gate': 'メインゲート'
        })
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('既に使用されています', data['message'])
        
        # 入場記録が1件だけであることを確認
        entry_count = Entry.objects.filter(ticket=self.ticket).count()
        self.assertEqual(entry_count, 1)
    
    def test_invalid_ticket_number(self):
        """無効なチケット番号のテスト"""
        # スタッフとしてログイン
        self.client.login(username='staff_user', password='testpass123')
        
        # 存在しないチケット番号で検証
        response = self.client.post(reverse('entries:verify_ticket'), {
            'ticket_number': 'INVALID-TICKET-999',
            'gate': 'メインゲート'
        })
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('チケットが見つかりません', data['message'])
        
        # 入場記録が作成されていないことを確認
        entry_count = Entry.objects.count()
        self.assertEqual(entry_count, 0)
    
    def test_cancelled_ticket_entry(self):
        """キャンセル済みチケットの入場テスト"""
        # スタッフとしてログイン
        self.client.login(username='staff_user', password='testpass123')
        
        # チケットをキャンセル
        self.ticket.status = 'cancelled'
        self.ticket.save()
        
        # 入場を試みる
        response = self.client.post(reverse('entries:verify_ticket'), {
            'ticket_number': self.ticket.ticket_number,
            'gate': 'メインゲート'
        })
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('キャンセルされています', data['message'])
    
    def test_entry_status_display(self):
        """入場状況表示テスト"""
        # スタッフとしてログイン
        self.client.login(username='staff_user', password='testpass123')
        
        # 入場記録を作成
        Entry.objects.create(
            ticket=self.ticket,
            gate='メインゲート',
            scanned_by=self.staff_user
        )
        
        # 入場状況ページにアクセス
        response = self.client.get(reverse('entries:entry_status'))
        self.assertEqual(response.status_code, 200)
        
        # 統計情報が含まれていることを確認
        self.assertIn('stats', response.context)
        self.assertEqual(response.context['stats']['total_entries'], 1)
    
    def test_unauthorized_access(self):
        """権限のないユーザーのアクセステスト"""
        # 一般ユーザーとしてログイン
        self.client.login(username='customer', password='testpass123')
        
        # QRスキャン画面にアクセス（失敗）
        response = self.client.get(reverse('entries:qr_scan'))
        # スタッフ権限が必要なため、ログインページまたは403にリダイレクト
        self.assertNotEqual(response.status_code, 200)
    
    def test_multiple_gates_entry(self):
        """複数ゲートでの入場テスト"""
        # スタッフとしてログイン
        self.client.login(username='staff_user', password='testpass123')
        
        # メインゲートで入場
        response = self.client.post(reverse('entries:verify_ticket'), {
            'ticket_number': self.ticket.ticket_number,
            'gate': 'メインゲート'
        })
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # 入場記録のゲート情報を確認
        entry = Entry.objects.filter(ticket=self.ticket).first()
        self.assertEqual(entry.gate, 'メインゲート')
