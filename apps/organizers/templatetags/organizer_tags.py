"""主催者用テンプレートタグ"""
from django import template

register = template.Library()


@register.filter
def sum_sales(event_sales):
    """売上合計を計算"""
    return sum(item['total_sales'] for item in event_sales)


@register.filter
def sum_tickets(event_sales):
    """販売枚数合計を計算"""
    return sum(item['total_tickets'] for item in event_sales)
