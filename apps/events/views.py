from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Venue, Event, TicketType
from .forms import VenueForm, EventForm, TicketTypeForm


# ================== 会場管理 ==================

class VenueListView(LoginRequiredMixin, ListView):
    """会場一覧ビュー"""
    model = Venue
    template_name = 'events/venue_list.html'
    context_object_name = 'venues'
    paginate_by = 20


class VenueCreateView(LoginRequiredMixin, CreateView):
    """会場登録ビュー"""
    model = Venue
    form_class = VenueForm
    template_name = 'events/venue_form.html'
    success_url = reverse_lazy('events:venue_list')
    
    def form_valid(self, form):
        messages.success(self.request, '会場を登録しました。')
        return super().form_valid(form)


class VenueUpdateView(LoginRequiredMixin, UpdateView):
    """会場編集ビュー"""
    model = Venue
    form_class = VenueForm
    template_name = 'events/venue_form.html'
    success_url = reverse_lazy('events:venue_list')
    
    def form_valid(self, form):
        messages.success(self.request, '会場を更新しました。')
        return super().form_valid(form)


class VenueDeleteView(LoginRequiredMixin, DeleteView):
    """会場削除ビュー"""
    model = Venue
    template_name = 'events/venue_confirm_delete.html'
    success_url = reverse_lazy('events:venue_list')
    
    def form_valid(self, form):
        messages.success(self.request, '会場を削除しました。')
        return super().form_valid(form)


# ================== イベント管理 ==================

class EventListView(LoginRequiredMixin, ListView):
    """イベント一覧ビュー（主催者向け）"""
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 20
    
    def get_queryset(self):
        # 主催者自身のイベントのみ表示
        if hasattr(self.request.user, 'organizer'):
            return Event.objects.filter(organizer=self.request.user.organizer)
        return Event.objects.none()


class EventCreateView(LoginRequiredMixin, CreateView):
    """イベント登録ビュー"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')
    
    def form_valid(self, form):
        # organizerを自動設定
        if hasattr(self.request.user, 'organizer'):
            form.instance.organizer = self.request.user.organizer
            messages.success(self.request, 'イベントを登録しました。')
            return super().form_valid(form)
        else:
            messages.error(self.request, '主催者アカウントが必要です。')
            return redirect('events:event_list')


class EventUpdateView(LoginRequiredMixin, UpdateView):
    """イベント編集ビュー"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')
    
    def get_queryset(self):
        # 主催者自身のイベントのみ編集可能
        if hasattr(self.request.user, 'organizer'):
            return Event.objects.filter(organizer=self.request.user.organizer)
        return Event.objects.none()
    
    def form_valid(self, form):
        messages.success(self.request, 'イベントを更新しました。')
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, DeleteView):
    """イベント削除ビュー"""
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event_list')
    
    def get_queryset(self):
        # 主催者自身のイベントのみ削除可能
        if hasattr(self.request.user, 'organizer'):
            return Event.objects.filter(organizer=self.request.user.organizer)
        return Event.objects.none()
    
    def form_valid(self, form):
        messages.success(self.request, 'イベントを削除しました。')
        return super().form_valid(form)


# ================== チケット種別管理 ==================

class TicketTypeCreateView(LoginRequiredMixin, CreateView):
    """チケット種別登録ビュー"""
    model = TicketType
    form_class = TicketTypeForm
    template_name = 'events/tickettype_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs['event_id'])
        # 主催者チェック
        if hasattr(request.user, 'organizer') and self.event.organizer == request.user.organizer:
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, '権限がありません。')
        return redirect('events:event_list')
    
    def form_valid(self, form):
        form.instance.event = self.event
        messages.success(self.request, 'チケット種別を登録しました。')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('events:event_detail', kwargs={'pk': self.event.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context


class TicketTypeUpdateView(LoginRequiredMixin, UpdateView):
    """チケット種別編集ビュー"""
    model = TicketType
    form_class = TicketTypeForm
    template_name = 'events/tickettype_form.html'
    
    def get_queryset(self):
        # 主催者自身のイベントのチケット種別のみ編集可能
        if hasattr(self.request.user, 'organizer'):
            return TicketType.objects.filter(event__organizer=self.request.user.organizer)
        return TicketType.objects.none()
    
    def form_valid(self, form):
        messages.success(self.request, 'チケット種別を更新しました。')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('events:event_detail', kwargs={'pk': self.object.event.pk})


class TicketTypeDeleteView(LoginRequiredMixin, DeleteView):
    """チケット種別削除ビュー"""
    model = TicketType
    template_name = 'events/tickettype_confirm_delete.html'
    
    def get_queryset(self):
        # 主催者自身のイベントのチケット種別のみ削除可能
        if hasattr(self.request.user, 'organizer'):
            return TicketType.objects.filter(event__organizer=self.request.user.organizer)
        return TicketType.objects.none()
    
    def form_valid(self, form):
        messages.success(self.request, 'チケット種別を削除しました。')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('events:event_detail', kwargs={'pk': self.object.event.pk})



# ================== 購入者向けイベント検索・詳細 ==================

class PublicEventListView(ListView):
    """購入者向けイベント一覧ビュー"""
    model = Event
    template_name = 'events/public_event_list.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Event.objects.filter(is_public=True).select_related('venue', 'organizer__user')
        
        # 検索クエリ
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(venue__name__icontains=search_query)
            )
        
        # カテゴリ絞り込み
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        
        # 日付順にソート
        queryset = queryset.order_by('start_datetime')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['categories'] = Event.CATEGORY_CHOICES
        return context


class EventDetailView(DetailView):
    """購入者向けイベント詳細ビュー"""
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        # 公開イベントのみ表示
        return Event.objects.filter(is_public=True).select_related('venue', 'organizer__user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # チケット種別を販売中のものから取得
        now = timezone.now()
        context['ticket_types'] = self.object.ticket_types.filter(
            sale_start__lte=now,
            sale_end__gte=now
        ).order_by('price')
        return context
