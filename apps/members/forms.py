"""会員管理フォーム"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """会員登録フォーム"""
    email = forms.EmailField(
        label='メールアドレス',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'})
    )
    username = forms.CharField(
        label='ユーザー名',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ユーザー名'})
    )
    first_name = forms.CharField(
        label='名',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '太郎'})
    )
    last_name = forms.CharField(
        label='姓',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '山田'})
    )
    phone_number = forms.CharField(
        label='電話番号',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '090-1234-5678'})
    )
    birth_date = forms.DateField(
        label='生年月日',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    password1 = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワード'})
    )
    password2 = forms.CharField(
        label='パスワード（確認）',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワード（確認）'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'birth_date', 'password1', 'password2']


class UserLoginForm(AuthenticationForm):
    """ログインフォーム"""
    username = forms.CharField(
        label='ユーザー名またはメールアドレス',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ユーザー名またはメールアドレス'})
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワード'})
    )


class UserProfileForm(forms.ModelForm):
    """会員情報編集フォーム"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'first_name': '名',
            'last_name': '姓',
            'email': 'メールアドレス',
            'phone_number': '電話番号',
            'birth_date': '生年月日',
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム（現在のパスワード確認付き）"""
    old_password = forms.CharField(
        label='現在のパスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '現在のパスワード'})
    )
    new_password1 = forms.CharField(
        label='新しいパスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '新しいパスワード'})
    )
    new_password2 = forms.CharField(
        label='新しいパスワード（確認）',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '新しいパスワード（確認）'})
    )


class PasswordResetRequestForm(forms.Form):
    """パスワードリセット申請フォーム"""
    email = forms.EmailField(
        label='登録メールアドレス',
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    """パスワードリセット確認フォーム"""
    new_password1 = forms.CharField(
        label='新しいパスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '新しいパスワード'})
    )
    new_password2 = forms.CharField(
        label='新しいパスワード（確認）',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '新しいパスワード（確認）'})
    )
