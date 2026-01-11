from django.db import models
from django.conf import settings
from apps.tickets.models import Ticket


class Entry(models.Model):
    """入場記録モデル"""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='entries',
        verbose_name='チケット'
    )
    
    gate = models.CharField('ゲート', max_length=50)
    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='scanned_entries',
        verbose_name='スキャンスタッフ'
    )
    
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
