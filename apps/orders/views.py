from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
import json
from .models import Cart, CartItem, Order, Payment
from apps.seats.models import Seat


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
