from django.db.models import Q, Count, Prefetch, OuterRef, Subquery, Max, F, Value
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models.core import WfOrderLog, WfDFXVersionControlLog, WfCutLog
from .models.stage import WfStageList


class OrderListView(LoginRequiredMixin, ListView):

    http_method_names = ['get', 'head', 'options', 'trace']

    queryset = WfOrderLog.objects.all()
    ordering = ['priority', '-start_date', 'deadline_date',]

    context_object_name = 'orders'
    
    template_name = 'workflow/dfx_log_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        work_groups = self.request.user.work_groups.all().values_list('group__name', flat=True)
        
        filter_arg = Q()
        prefetch_related = []
        
        print(work_groups)
        
        if 'dfx_version_control' in work_groups:
            filter_arg &= (Q(start_manufacturing=True) & Q(dfx_logs__isnull=False) & (Q(dfx_logs__user=self.request.user) & Q(dfx_logs__user__isnull=True)))
            prefetch_related.append(Prefetch('dfx_logs', WfDFXVersionControlLog.objects.select_related('stage', 'status', 'user')))
        elif 'cut' in work_groups:
            filter_arg &= (Q(start_manufacturing=True) & Q(cut_logs__isnull=False) & (Q(cut_logs__user=self.request.user) | Q(cut_logs__user__isnull=True)))
            prefetch_related.append(Prefetch('cut_logs', WfCutLog.objects.select_related('stage', 'status', 'user')))
        
        queryset = queryset.filter(filter_arg) \
                    .defer('delivery', 'mobile_number', 'email', 'payment').distinct()
        
        select_related = [
            'model', 
            'configuration', 
            'fireclay_type', 
            'glazing_type', 
            'frame_type', 
            'priority'
        ]
        
        # TODO: annotate queries to increase performance
        
        # dfx_logs = WfDFXVersionControlLog.objects.values('order') \
        #                                          .annotate(max_date=Max('created_at')) \
        #                                          .filter((Q(user=self.request.user) | Q(user__isnull=True))) \
        #                                          .annotate(some=Value(1))
                                                 
                        
        # print(dfx_logs)

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
def switch_job(request, order_id, stage_id):
    order = get_object_or_404(WfOrderLog, id=order_id)
    
    stage = WfStageList.objects.get(id=stage_id)
    work_groups = request.user.work_groups.all().values_list('group__name', flat=True)
        
    if 'dfx_version_control' in work_groups:
        order.dfx_logs.create(user=request.user, stage=stage)
    elif 'cut' in work_groups:
        order.cut_logs.create(user=request.user, stage=stage)
    
    return render(request, 'workflow/order.html', { 'order': order })

