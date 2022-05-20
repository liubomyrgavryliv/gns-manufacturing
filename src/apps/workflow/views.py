from django.db.models import Q, Prefetch,F, Window
from django.db.models.functions import Rank
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, UpdateView, DetailView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models.core import WfOrderLog, WfDFXVersionControlLog, WfCutLog, WfBendLog, WfWeldLog, WfLocksmithLog, WfNoteLog
from .models.stage import WfStageList


class OrderListView(LoginRequiredMixin, ListView):

    http_method_names = ['get', 'head', 'options', 'trace']

    queryset = WfOrderLog.objects.all()
    ordering = ['priority', '-start_date', 'deadline_date',]

    context_object_name = 'orders'
    
    template_name = 'workflow/order/list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        principal_groups = self.kwargs.get('principal_groups', [])
        work_groups = self.kwargs.get('work_groups', [])
        
        filter_arg = Q()
        prefetch_related = []
        logs = []
        
        if 'lead' in principal_groups:
            filter_arg &= (Q(start_manufacturing=True))
            prefetch_related.append(Prefetch('dfx_logs', WfDFXVersionControlLog.objects.select_related('stage', 'status', 'user')))
            prefetch_related.append(Prefetch('cut_logs', WfCutLog.objects.select_related('stage', 'status', 'user')))
            
            select_related = [
                'model', 
                'configuration', 
                'fireclay_type', 
                'glazing_type', 
                'frame_type', 
                'priority',
            ]
        else:
            select_related = [
                'order__model', 
                'order__configuration', 
                'order__fireclay_type', 
                'order__glazing_type', 
                'order__frame_type', 
                'order__priority',
            ]
            
            if 'dfx_version_control' in work_groups:
                logs_ = WfDFXVersionControlLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('order'),
                            order_by=F('created_at').desc(),
                        ),
                ).filter((Q(user=self.request.user) | Q(user__isnull=True)))

                sql, params = logs_.query.sql_with_params()
                dfx_logs = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                queryset = WfDFXVersionControlLog.objects.filter(Q(id__in=[log_.id for log_ in dfx_logs]) & Q(order__start_manufacturing=True))
        
            elif 'cut' in work_groups:
                logs_ = WfCutLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('order'),
                            order_by=F('created_at').desc(),
                        ),
                ).filter((Q(user=self.request.user) | Q(user__isnull=True)))

                sql, params = logs_.query.sql_with_params()
                cut_logs = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                queryset = WfCutLog.objects.filter(Q(id__in=[log_.id for log_ in cut_logs]) & Q(order__start_manufacturing=True))
                
            elif 'bend' in work_groups:
                logs_ = WfCutLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('order'),
                            order_by=F('created_at').desc(),
                        ),
                ).filter((Q(user=self.request.user) | Q(user__isnull=True)))

                sql, params = logs_.query.sql_with_params()
                cut_logs = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                logs = WfCutLog.objects.filter(Q(id__in=[log_.id for log_ in cut_logs]) )
                
                prefetch_related.append(Prefetch('cut_logs', logs.select_related('stage', 'status', 'user')))
                filter_arg &= (Q(start_manufacturing=True) & Q(cut_logs__in=logs))
                
            elif 'weld' in work_groups:
                logs_ = WfWeldLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('order'),
                            order_by=F('created_at').desc(),
                        ),
                ).filter((Q(user=self.request.user) | Q(user__isnull=True)))

                sql, params = logs_.query.sql_with_params()
                weld_logs = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                logs = WfWeldLog.objects.filter(Q(id__in=[log_.id for log_ in weld_logs]) )
                
                prefetch_related.append(Prefetch('weld_logs', logs.select_related('stage', 'status', 'user')))
                filter_arg &= (Q(start_manufacturing=True) & Q(weld_logs__in=logs))
                
            elif 'locksmith' in work_groups:
                logs_ = WfLocksmithLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('order'),
                            order_by=F('created_at').desc(),
                        ),
                ).filter((Q(user=self.request.user) | Q(user__isnull=True)))

                sql, params = logs_.query.sql_with_params()
                locksmith_logs = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                logs = WfWeldLog.objects.filter(Q(id__in=[log_.id for log_ in locksmith_logs]) )
                
                prefetch_related.append(Prefetch('locksmith_logs', logs.select_related('stage', 'status', 'user')))
                filter_arg &= (Q(start_manufacturing=True) & Q(locksmith_logs__in=logs))
                
            else:
                raise PermissionDenied

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        
        return queryset

    
    def get_template_names(self):
        template = super().get_template_names()
        
        principal_groups = self.kwargs.get('principal_groups', [])
        
        if 'lead' in principal_groups:
            template = 'workflow/full_log/list.html'
        else:
            pass
        
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



class OrderDetailView(PermissionRequiredMixin, DetailView):
    
    http_method_names = ['get', 'head', 'options', 'trace']
    
    permission_required = ('workflow.view_wforderlog',)
    
    context_object_name = 'order'
    model = WfOrderLog
    
    template_name = 'workflow/order_detail.html'
    
    
    
class OrderUpdateView(PermissionRequiredMixin, UpdateView):
    
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'trace']
    
    permission_required = ('workflow.view_wforderlog', 'workflow.change_wforderlog',)
    
    model = WfOrderLog
    fields = ['model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type',]
    
    template_name = 'workflow/order_update.html'
    
    
    
class NoteListView(LoginRequiredMixin, ListView):
    
    http_method_names = ['get', 'head', 'options', 'trace']
    
    ordering = ['order', '-created_at',]

    context_object_name = 'notes'
    
    queryset = WfNoteLog.objects.all()
    
    template_name = 'workflow/note/list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        queryset = queryset.filter(order=self.kwargs.get('pk'))
        
        queryset = queryset.select_related('order', 'user')
        
        return queryset
    

@login_required
@require_POST
def switch_job(request, log_id, stage_id):
    
    stage = WfStageList.objects.get(id=stage_id)
    work_groups = request.user.work_groups.all().values_list('group__name', flat=True)
    
    template = 'workflow/order/order.html'
        
    try:
        if 'dfx_version_control' in work_groups: 
            log = get_object_or_404(WfDFXVersionControlLog, id=log_id)
            if request.user == log.user or log.user is None:

                order = WfDFXVersionControlLog.objects.create(order=log.order, user=request.user, stage=stage)
            
            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'cut' in work_groups: 
            log = get_object_or_404(WfCutLog, id=log_id)
            if request.user == log.user or log.user is None:

                order = WfCutLog.objects.create(order=log.order, user=request.user, stage=stage)

            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'weld' in work_groups: 
            log = get_object_or_404(WfWeldLog, id=log_id)
            if request.user == log.user or log.user is None:

                order = WfWeldLog.objects.create(order=log.order, user=request.user, stage=stage)

            else:
                raise Exception('The user is allowed to edit only his entries!')
        else:
            pass

    except Exception as e:
        raise Exception(e)
    
    return render(request, template, { 'order': order })
