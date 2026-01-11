from django import forms
from .models import Venue, Event, TicketType


class VenueForm(forms.ModelForm):
    """会場登録・編集フォーム"""
    
    class Meta:
        model = Venue
        fields = ['name', 'address', 'capacity', 'seat_map_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '東京ドーム'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '東京都文京区...'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '55000'}),
            'seat_map_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '会場名',
            'address': '住所',
            'capacity': '収容人数',
            'seat_map_image': '座席図画像（オプション）',
        }


class EventForm(forms.ModelForm):
    """イベント登録・編集フォーム"""
    
    class Meta:
        model = Event
        fields = ['name', 'description', 'category', 'venue', 'start_datetime', 
                  'end_datetime', 'image', 'is_public', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'venue': forms.Select(attrs={'class': 'form-select'}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class TicketTypeForm(forms.ModelForm):
    """チケット種別登録・編集フォーム"""
    
    class Meta:
        model = TicketType
        fields = ['name', 'type', 'price', 'total_quantity', 'sale_start', 'sale_end']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'S席'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_start': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'sale_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
