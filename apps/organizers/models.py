from django.db import models
from apps.members.models import User


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

