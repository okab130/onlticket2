"""会員管理ビュー"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from apps.members.forms import (
    UserRegistrationForm, 
    UserLoginForm, 
    UserProfileForm,
    CustomPasswordChangeForm,
    PasswordResetRequestForm,
    CustomSetPasswordForm
)
from apps.orders.models import Order

User = get_user_model()


def register_view(request):
    """会員登録"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '会員登録が完了しました。')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'members/register.html', {'form': form})


def login_view(request):
    """ログイン"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        
        # アカウントロックチェック
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            if user.account_locked_until and user.account_locked_until > timezone.now():
                messages.error(request, f'アカウントがロックされています。{user.account_locked_until.strftime("%Y年%m月%d日 %H:%M")}まで待ってください。')
                return render(request, 'members/login.html', {'form': form})
        except User.DoesNotExist:
            pass
        
        if form.is_valid():
            user = form.get_user()
            
            # ログイン成功時にfailed_login_attemptsをリセット
            user.failed_login_attempts = 0
            user.last_failed_login = None
            user.account_locked_until = None
            user.save()
            
            login(request, user)
            messages.success(request, 'ログインしました。')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            # ログイン失敗時の処理（Brute force対策）
            try:
                user = User.objects.get(username=username)
                user.failed_login_attempts += 1
                user.last_failed_login = timezone.now()
                
                # 5回失敗でアカウントロック（30分間）
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
                    messages.error(request, 'ログイン失敗回数が上限に達しました。30分間アカウントがロックされます。')
                else:
                    remaining = 5 - user.failed_login_attempts
                    messages.error(request, f'ログインに失敗しました。残り{remaining}回失敗するとアカウントがロックされます。')
                
                user.save()
            except User.DoesNotExist:
                messages.error(request, 'ログインに失敗しました。')
    else:
        form = UserLoginForm()
    
    return render(request, 'members/login.html', {'form': form})


@require_http_methods(["POST"])
def logout_view(request):
    """ログアウト"""
    logout(request)
    messages.success(request, 'ログアウトしました。')
    return redirect('home')


@login_required
def profile_view(request):
    """マイページ - プロフィール表示"""
    return render(request, 'members/profile.html', {'user': request.user})


@login_required
def profile_edit_view(request):
    """会員情報編集"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '会員情報を更新しました。')
            return redirect('members:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'members/profile_edit.html', {'form': form})


@login_required
def purchase_history_view(request):
    """購入履歴"""
    orders = Order.objects.filter(user=request.user).select_related('event').prefetch_related('tickets').order_by('-created_at')
    return render(request, 'members/purchase_history.html', {'orders': orders})


@login_required
def password_change_view(request):
    """パスワード変更"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'パスワードを変更しました。')
            return redirect('members:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'members/password_change.html', {'form': form})


def password_reset_request_view(request):
    """パスワードリセット申請"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(
                    reverse('members:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                
                send_mail(
                    subject='パスワードリセット申請',
                    message=f'以下のURLからパスワードをリセットしてください。\n\n{reset_url}\n\nこのリンクは24時間有効です。',
                    from_email=None,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, 'パスワードリセット用のメールを送信しました。')
            except User.DoesNotExist:
                messages.success(request, 'パスワードリセット用のメールを送信しました。')
            
            return redirect('home')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'members/password_reset_request.html', {'form': form})


def password_reset_confirm_view(request, uidb64, token):
    """パスワードリセット確認"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'パスワードをリセットしました。新しいパスワードでログインしてください。')
                return redirect('members:login')
        else:
            form = CustomSetPasswordForm(user)
        
        return render(request, 'members/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'パスワードリセットリンクが無効です。')
        return redirect('home')
