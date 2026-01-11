from django import forms


class SeatBulkCreateForm(forms.Form):
    """座席一括登録フォーム"""
    
    SEAT_TYPE_CHOICES = [
        ('S', 'S席'),
        ('A', 'A席'),
        ('B', 'B席'),
    ]
    
    block = forms.CharField(
        label='ブロック',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A'})
    )
    
    seat_type = forms.ChoiceField(
        label='座席種別',
        choices=SEAT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    row_start = forms.CharField(
        label='開始列',
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1'})
    )
    
    row_end = forms.CharField(
        label='終了列',
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10'})
    )
    
    number_start = forms.IntegerField(
        label='開始番号',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1'})
    )
    
    number_end = forms.IntegerField(
        label='終了番号',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20'})
    )
