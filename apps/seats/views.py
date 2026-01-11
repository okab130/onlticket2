from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from apps.events.models import Venue
from .models import Seat
from .forms import SeatBulkCreateForm
from .services import generate_seats


class SeatBulkCreateView(LoginRequiredMixin, View):
    """座席一括登録ビュー"""
    
    def get(self, request, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        form = SeatBulkCreateForm()
        return render(request, 'seats/seat_creation.html', {
            'venue': venue,
            'form': form,
        })
    
    def post(self, request, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        form = SeatBulkCreateForm(request.POST)
        
        if form.is_valid():
            try:
                created_seats = generate_seats(
                    venue=venue,
                    block=form.cleaned_data['block'],
                    seat_type=form.cleaned_data['seat_type'],
                    row_start=form.cleaned_data['row_start'],
                    row_end=form.cleaned_data['row_end'],
                    number_start=form.cleaned_data['number_start'],
                    number_end=form.cleaned_data['number_end'],
                )
                messages.success(request, f'{len(created_seats)}件の座席を登録しました。')
                return redirect('seats:seat_list', venue_id=venue.pk)
            except Exception as e:
                messages.error(request, f'座席登録に失敗しました: {str(e)}')
        
        return render(request, 'seats/seat_creation.html', {
            'venue': venue,
            'form': form,
        })


class SeatListView(LoginRequiredMixin, ListView):
    """座席一覧ビュー"""
    model = Seat
    template_name = 'seats/seat_list.html'
    context_object_name = 'seats'
    paginate_by = 100
    
    def get_queryset(self):
        venue_id = self.kwargs.get('venue_id')
        return Seat.objects.filter(venue_id=venue_id).order_by('block', 'row', 'number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        venue_id = self.kwargs.get('venue_id')
        context['venue'] = get_object_or_404(Venue, pk=venue_id)
        return context


class SeatDeleteView(LoginRequiredMixin, DeleteView):
    """座席削除ビュー"""
    model = Seat
    template_name = 'seats/seat_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('seats:seat_list', kwargs={'venue_id': self.object.venue.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '座席を削除しました。')
        return super().form_valid(form)



class SeatSelectionView(View):
    """座席選択ビュー"""
    
    def get(self, request, event_id, ticket_type_id):
        from apps.events.models import Event, TicketType
        from .services import get_available_seats_json
        from django.http import JsonResponse
        
        event = get_object_or_404(Event, pk=event_id, is_public=True)
        ticket_type = get_object_or_404(TicketType, pk=ticket_type_id, event=event)
        
        # Ajax リクエストの場合はJSON返却
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            seats_data = get_available_seats_json(event, ticket_type)
            return JsonResponse({'seats': seats_data})
        
        # 通常リクエストの場合はテンプレート表示
        return render(request, 'seats/seat_selection.html', {
            'event': event,
            'ticket_type': ticket_type,
        })
