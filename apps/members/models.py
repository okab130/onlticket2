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

