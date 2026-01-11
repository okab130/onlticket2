from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
import json
from .models import Cart, CartItem, Order, Payment, Cancellation
from apps.seats.models import Seat
from apps.events.models import TicketType


class AddToCartView(LoginRequiredMixin, View):
    """カートに追加"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            seat_ids = data.get('seat_ids', [])
            
            if not seat_ids:
                return JsonResponse({'error': 'No seats selected'}, status=400)
            
            with transaction.atomic():
                # カート取得または作成
                cart, created = Cart.objects.get_or_create(user=request.user)
                
                # 座席をロックして追加
                for seat_id in seat_ids:
                    seat = Seat.objects.select_for_update().get(
                        id=seat_id,
                        status='available'
                    )
                    
                    # カートに追加
                    CartItem.objects.create(cart=cart, seat=seat)
                    
                    # 座席を予約中に変更
                    seat.status = 'reserved'
                    seat.reserved_by = request.user
                    seat.save()
            
            return JsonResponse({'success': True})
            
        except Seat.DoesNotExist:
            return JsonResponse({'error': 'Seat not available'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CartView(LoginRequiredMixin, View):
    """カート表示"""
    
    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.select_related('seat__venue').all()
        except Cart.DoesNotExist:
            cart = None
            cart_items = []
        
        return render(request, 'orders/cart.html', {
            'cart': cart,
            'cart_items': cart_items,
        })


class RemoveFromCartView(LoginRequiredMixin, View):
    """カートから削除"""
    
    def post(self, request, item_id):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            
            with transaction.atomic():
                # 座席を空席に戻す
                seat = cart_item.seat
                seat.status = 'available'
                seat.reserved_by = None
                seat.save()
                
                # カートアイテム削除
                cart_item.delete()
            
            messages.success(request, '座席をカートから削除しました。')
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'カートアイテムが見つかりません。')
        
        return redirect('orders:cart')



class CheckoutView(LoginRequiredMixin, View):
    """購入確認・確定"""
    
    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.select_related('seat__venue').all()
            
            if not cart_items:
                messages.warning(request, 'カートが空です。')
                return redirect('orders:cart')
            
        except Cart.DoesNotExist:
            messages.warning(request, 'カートが空です。')
            return redirect('orders:cart')
        
        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'cart_items': cart_items,
        })
    
    def post(self, request):
        from .services import create_order
        
        try:
            cart = Cart.objects.get(user=request.user)
            
            # 購入確定処理
            order = create_order(user=request.user, cart=cart)
            
            messages.success(request, f'購入が完了しました。注文番号: {order.order_number}')
            return redirect('orders:purchase_complete', order_number=order.order_number)
            
        except Cart.DoesNotExist:
            messages.error(request, 'カートが見つかりません。')
            return redirect('orders:cart')
        except Exception as e:
            messages.error(request, f'購入処理に失敗しました: {str(e)}')
            return redirect('orders:cart')


class PurchaseCompleteView(LoginRequiredMixin, View):
    """購入完了画面"""
    
    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        
        return render(request, 'orders/purchase_complete.html', {
            'order': order,
        })


@login_required
def add_to_cart_free_view(request):
    """自由席チケットをカートに追加"""
    if request.method == 'POST':
        ticket_type_id = request.POST.get('ticket_type_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            ticket_type = get_object_or_404(TicketType, pk=ticket_type_id, type='free')
            
            # 在庫チェック
            if ticket_type.remaining_quantity < quantity:
                messages.error(request, '指定された枚数が在庫を超えています。')
                return redirect('events:event_detail', pk=ticket_type.event.pk)
            
            with transaction.atomic():
                # カート取得または作成
                cart, created = Cart.objects.get_or_create(user=request.user)
                
                # 自由席チケットをカートに追加（seat=Nullで管理）
                # 注: CartItemモデルにticket_typeとquantityフィールドが必要
                # 簡易実装として、枚数分のCartItemを作成
                for _ in range(quantity):
                    CartItem.objects.create(
                        cart=cart,
                        seat=None,
                        ticket_type=ticket_type
                    )
                
                # 販売済枚数を増加（仮予約）
                ticket_type.sold_quantity += quantity
                ticket_type.save()
            
            messages.success(request, f'{ticket_type.name} を {quantity}枚カートに追加しました。')
            return redirect('orders:cart')
            
        except Exception as e:
            messages.error(request, f'カートへの追加に失敗しました: {str(e)}')
            return redirect('events:event_detail', pk=ticket_type.event.pk)
    
    return redirect('events:public_event_list')


@login_required
def cancellation_request_view(request, order_id):
    """キャンセル申請"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    # すでにキャンセル申請済みの場合
    if hasattr(order, 'cancellation'):
        messages.warning(request, 'このチケットはすでにキャンセル申請済みです。')
        return redirect('members:purchase_history')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        if not reason:
            messages.error(request, 'キャンセル理由を入力してください。')
            return render(request, 'orders/cancellation_request.html', {'order': order})
        
        # キャンセル申請作成
        Cancellation.objects.create(
            order=order,
            reason=reason,
            refund_amount=order.total_amount,
            status='requested'
        )
        
        messages.success(request, 'キャンセル申請を受け付けました。承認をお待ちください。')
        return redirect('members:purchase_history')
    
    return render(request, 'orders/cancellation_request.html', {'order': order})
