from django.db.models import Q, Count, Prefetch, OuterRef, Subquery, Max, F, Value
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, UpdateView, DetailView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models.core import WfOrderLog, WfDFXVersionControlLog, WfCutLog, WfBendLog, WfWeldLog, WfLocksmithLog
from .models.stage import WfStageList


class OrderListView(LoginRequiredMixin, ListView):

    http_method_names = ['get', 'head', 'options', 'trace']

    queryset = WfOrderLog.objects.all()
    ordering = ['priority', '-start_date', 'deadline_date',]

    context_object_name = 'orders'
    
    template_name = 'workflow/full_log/list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        principal_groups = self.kwargs.get('principal_groups', [])
        work_groups = self.kwargs.get('work_groups', [])
        
        filter_arg = Q()
        prefetch_related = []
        
        if 'lead' in principal_groups:
            filter_arg &= (Q(start_manufacturing=True))
            prefetch_related.append(Prefetch('dfx_logs', WfDFXVersionControlLog.objects.select_related('stage', 'status', 'user')))
            prefetch_related.append(Prefetch('cut_logs', WfCutLog.objects.select_related('stage', 'status', 'user')))
        else:
            if 'dfx_version_control' in work_groups:
                filter_arg &= (Q(start_manufacturing=True) & Q(dfx_logs__isnull=False) & (Q(dfx_logs__user=self.request.user) | Q(dfx_logs__user__isnull=True)))
                prefetch_related.append(Prefetch('dfx_logs', WfDFXVersionControlLog.objects.select_related('stage', 'status', 'user')))
            elif 'cut' in work_groups:
                filter_arg &= (Q(start_manufacturing=True) & Q(cut_logs__isnull=False) & (Q(cut_logs__user=self.request.user) | Q(cut_logs__user__isnull=True)))
                prefetch_related.append(Prefetch('cut_logs', WfCutLog.objects.select_related('stage', 'status', 'user')))
            elif 'bend' in work_groups:
                filter_arg &= (Q(start_manufacturing=True) & Q(bend_logs__isnull=False) & (Q(bend_logs__user=self.request.user) | Q(bend_logs__user__isnull=True)))
                prefetch_related.append(Prefetch('bend_logs', WfBendLog.objects.select_related('stage', 'status', 'user')))
            elif 'weld' in work_groups:
                filter_arg &= (Q(start_manufacturing=True) & Q(weld_logs__isnull=False) & (Q(weld_logs__user=self.request.user) | Q(weld_logs__user__isnull=True)))
                prefetch_related.append(Prefetch('weld_logs', WfWeldLog.objects.select_related('stage', 'status', 'user')))
            elif 'locksmith' in work_groups:
                filter_arg &= (Q(start_manufacturing=True) & Q(locksmith_logs__isnull=False) & (Q(locksmith_logs__user=self.request.user) | Q(locksmith_logs__user__isnull=True)))
                prefetch_related.append(Prefetch('locksmith_logs', WfLocksmithLog.objects.select_related('stage', 'status', 'user')))
            else:
                raise PermissionDenied
            
        queryset = queryset.filter(filter_arg).defer('delivery', 'mobile_number', 'email', 'payment').distinct()
        
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
    
    
    def get_template_names(self):
        template = super().get_template_names()
        
        principal_groups = self.kwargs.get('principal_groups', [])
        work_groups = self.kwargs.get('work_groups', [])
        
        if 'lead' in principal_groups:
            pass
        else:
            if 'dfx_version_control' in work_groups:
                template = 'workflow/dfx_log/list.html'
            elif 'cut' in work_groups:
                template = 'workflow/cut_log/list.html'
            elif 'bend' in work_groups:
                template = 'workflow/bend_log/list.html'
            elif 'weld' in work_groups:
                template = 'workflow/weld_log/list.html'
            elif 'locksmith' in work_groups:
                template = 'workflow/locksmith_log/list.html'
            else:
                raise PermissionDenied
        
        return template


    def get_ordering(self):
        ordering = super().get_ordering()
    
        # TODO: sort by stage of a specific log, depending on user group
        return ordering
    
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        
        if not self.request.user.is_anonymous:
            try:
                work_groups = self.request.user.work_groups.all().values_list('group__name', flat=True)
                principal_groups = self.request.user.groups.all().values_list('name', flat=True)
                
                self.kwargs['work_groups'] = work_groups
                self.kwargs['principal_groups'] = principal_groups
            except Exception as e:
                raise Exception(e)
        else:
            pass



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
    
    template = None
        
    try:
        if 'dfx_version_control' in work_groups: 
            if request.user == order.dfx_logs.all().last().user or order.dfx_logs.all().last().user is None:
                order.dfx_logs.create(user=request.user, stage=stage)
                template = 'workflow/dfx_log/order.html'
            else:
                raise Exception('The user is allowed to edit only his entries!')
        elif 'cut' in work_groups:
            order.cut_logs.create(user=request.user, stage=stage)
            template = 'workflow/cut_log/order.html'
        elif 'bend' in work_groups:
            order.bend_logs.create(user=request.user, stage=stage)
            template = 'workflow/bend_log/order.html'
        elif 'weld' in work_groups:
            order.weld_logs.create(user=request.user, stage=stage)
            template = 'workflow/weld_log/order.html'
        elif 'locksmith' in work_groups:
            order.locksmith_logs.create(user=request.user, stage=stage)
            template = 'workflow/locksmith_log/order.html'
        else:
            pass

    except Exception as e:
        raise Exception(e)
    
    return render(request, template, { 'order': order })

