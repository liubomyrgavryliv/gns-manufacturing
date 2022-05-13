from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models.core import WfOrderLog, WfDFXVersionControlLog
from .models.stage import WfStageList


class OrderListView(LoginRequiredMixin, ListView):

    http_method_names = ['get', 'head', 'options', 'trace']

    queryset = WfOrderLog.objects.all()
    ordering = ['priority', '-start_date', 'deadline_date',]

    context_object_name = 'orders'
    
    template_name = 'workflow/dfx_log_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        queryset = queryset.filter(Q(start_manufacturing=True) | (Q(start_manufacturing=True) & Q(dfx_logs__user=self.request.user))) \
                    .defer('delivery', 'mobile_number', 'email', 'payment').distinct()
        
        select_related = [
            'model', 
            'configuration', 
            'fireclay_type', 
            'glazing_type', 
            'frame_type', 
            'priority'
        ]

        prefetch_related = [
            'dfx_logs',
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        
        return queryset


    def get_ordering(self):
        ordering = super().get_ordering()
    
        # TODO: sort by stage of a specific log, depending on user group
        return ordering


class OrderDetailView(LoginRequiredMixin, DetailView):
    
    http_method_names = ['get', 'head', 'options', 'trace']
    
    context_object_name = 'order'
    model = WfOrderLog
    
    template_name = 'workflow/order_detail.html'
    


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'trace']
    
    model = WfOrderLog
    fields = ['model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'note',]
    
    template_name = 'workflow/order_update.html'


@login_required
@require_POST
def start_job(request, id):
    order = get_object_or_404(WfOrderLog, id=id)
    
    # TODO: make a decision about where to add log based on request.user
    stage = WfStageList.objects.get(name='в роботі')
    order.dfx_logs.create(user=request.user, stage=stage)
    
    return render(request, 'workflow/order.html', { 'order': order })


@login_required
@require_POST
def finish_job(request, id):
    order = get_object_or_404(WfOrderLog, id=id)
    
    # TODO: make a decision about where to add log based on request.user
    stage = WfStageList.objects.get(name='виконано')
    order.dfx_logs.create(user=request.user, stage=stage)
        
    return render(request, 'workflow/order.html', { 'order': order })
