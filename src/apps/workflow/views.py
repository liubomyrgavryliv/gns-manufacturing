from django.db.models import Q, Prefetch,F, Window, Count, OuterRef, Subquery, Case, When, Value
from django.db.models.functions import Rank
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, UpdateView, DetailView, CreateView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import HttpResponse

from .models.core import WfOrderLog, WfOrderWorkStage, WfWorkLog, WfDXFVersionControlLog, WfCutLog, WfBendLog, WfWeldLog, WfLocksmithLog, WfNoteLog
from .models.stage import WfStageList
from .forms import WfNoteLogForm, WfOrderLogForm
from .queries import annotate_current_stage


class OrderListView(LoginRequiredMixin, ListView):

    http_method_names = ['get', 'head', 'options', 'trace',]

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
            prefetch_related.append(Prefetch('dxf_logs', WfDXFVersionControlLog.objects.select_related('stage', 'status', 'user')))
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
            # select_related = [
            #     'order__model', 
            #     'order__configuration', 
            #     'order__fireclay_type', 
            #     'order__glazing_type', 
            #     'order__frame_type', 
            #     'order__priority',
            # ]
            # prefetch_related = ['order__notes',]
            
            select_related = [
                'model', 
                'configuration', 
                'fireclay_type', 
                'glazing_type', 
                'frame_type', 
                'priority',
            ]
            prefetch_related = ['notes',]

            if 'dxf_version_control' in work_groups:
                
                                            
                logs_ = WfWorkLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('work_stage'),
                            order_by=F('created_at').desc(),
                        ),
                )

                sql, params = logs_.query.sql_with_params()
                work_log_id = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                work_log = WfWorkLog.objects.filter(
                                                Q(id__in=[log_.id for log_ in work_log_id]) & 
                                                Q(work_stage__order=OuterRef('id')) & 
                                                Q(work_stage__work_stage=1)
                                            ) \
                                            .annotate(
                                                username_=F('user__username'),
                                                stage_=F('stage__id')
                                            )
                
                
                queryset = WfOrderLog.objects.filter(Q(work_stages=1) & Q(start_manufacturing=True)) \
                                             .annotate(
                                                notes_count=Count('notes'),
                                                username=Subquery(work_log.values('username_')),
                                                stage_id=Subquery(work_log.values('stage_')),
                                                current_stage=Value('Триває')
                                             ) \
                                             .order_by('-priority__id')
        
            elif 'cut' in work_groups:
                
                logs_ = WfCutLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('order'),
                            order_by=F('created_at').desc(),
                        ),
                )

                sql, params = logs_.query.sql_with_params()
                cut_logs = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                queryset = WfCutLog.objects.annotate(notes=Count('order__notes')) \
                                           .filter(Q(id__in=[log_.id for log_ in cut_logs]) & Q(order__start_manufacturing=True)) \
                                           .order_by('-order__priority__id')
                
            elif 'bend' in work_groups:
                logs_ = WfBendLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('order'),
                            order_by=F('created_at').desc(),
                        ),
                )

                sql, params = logs_.query.sql_with_params()
                bend_logs = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                queryset = WfBendLog.objects.annotate(notes=Count('order__notes')) \
                                            .filter(Q(id__in=[log_.id for log_ in bend_logs]) & Q(order__start_manufacturing=True)) \
                                            .order_by('-order__priority__id')
                
            elif 'weld' in work_groups:
                logs_ = WfWeldLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('order'),
                            order_by=F('created_at').desc(),
                        ),
                )

                sql, params = logs_.query.sql_with_params()
                weld_logs = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                queryset = WfWeldLog.objects.annotate(notes=Count('order__notes')) \
                                            .filter(Q(id__in=[log_.id for log_ in weld_logs]) & Q(order__start_manufacturing=True)) \
                                            .order_by('-order__priority__id')
                
            elif 'locksmith' in work_groups:
                logs_ = WfLocksmithLog.objects.annotate(
                        rank_=Window(
                            expression=Rank(),
                            partition_by=F('order'),
                            order_by=F('created_at').desc(),
                        ),
                )

                sql, params = logs_.query.sql_with_params()
                locksmith_logs = logs_.raw(f"SELECT id FROM ({ sql }) AS full WHERE rank_ = 1;", params)
                
                queryset = WfLocksmithLog.objects.annotate(notes=Count('order__notes')) \
                                                 .filter(Q(id__in=[log_.id for log_ in locksmith_logs]) & Q(order__start_manufacturing=True)) \
                                                 .order_by('-order__priority__id')
                
            else:
                raise PermissionDenied

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        
        return queryset

    
    def get_template_names(self):
        template = super().get_template_names()
        
        principal_groups = self.kwargs.get('principal_groups', [])
        work_groups = self.kwargs.get('work_groups', [])
        
        if 'lead' in principal_groups:
            template = 'workflow/full_log/list.html'
        else:
            if 'dxf_version_control' in work_groups:
                template = 'workflow/dxf_log/list.html'
            elif any(x in ['cut', 'bend', 'weld', ] for x in work_groups):
                template = 'workflow/cut_bend_weld_log/list.html'
            elif 'locksmith' in work_groups:
                template = 'workflow/locksmith_log/list.html'
        
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
    fields = []
    
    template_name = 'workflow/order_update.html'
    success_url = '/orders/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.object.id
        return context
    
    
    def dispatch(self, request, *args, **kwargs):
        work_groups = request.user.work_groups.all().values_list('group__name', flat=True)
        if 'dxf_version_control' in work_groups:
            self.fields = ['priority', 'model', 'configuration', 'deadline_date',]
        return super().dispatch(request, *args, **kwargs)
    
    
    
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
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.kwargs.get('pk')
        return context


@login_required
def add_note(request, order_id):
    if request.method == "POST":
        form = WfNoteLogForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.order = WfOrderLog.objects.get(id=order_id)
            form.save()
            return HttpResponse(status=201, headers={'HX-Trigger': 'notesListChanged'})
    else:
        form = WfNoteLogForm()
    return render(request, 'workflow/note/create_form.html', { 'form': form, 'order_id': order_id })
    

@login_required
@require_POST
def switch_job(request, order_id, stage_id):
    
    stage = WfStageList.objects.get(id=stage_id)
    work_groups = request.user.work_groups.all().values_list('group__name', flat=True)
    
    template = 'workflow/order/order.html'
    create_obj = { 'user': request.user, 'stage': stage }
        
    try:
        if 'dxf_version_control' in work_groups: 
            order = get_object_or_404(WfOrderLog, id=order_id)
            work_stage = WfOrderWorkStage.objects.get(Q(order=order_id) & Q(work_stage=1))
            template = 'workflow/dxf_log/order.html'
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                WfWorkLog.objects.create(work_stage=work_stage, **create_obj)
            
            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'cut' in work_groups: 
            log = get_object_or_404(WfCutLog, id=log_id)
            template = 'workflow/cut_bend_weld_log/order.html'
            if request.user == log.user or log.user is None:

                order = WfCutLog.objects.create(order=log.order, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'bend' in work_groups: 
            log = get_object_or_404(WfBendLog, id=log_id)
            template = 'workflow/cut_bend_weld_log/order.html'
            if request.user == log.user or log.user is None:

                order = WfBendLog.objects.create(order=log.order, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')    
            
        elif 'weld' in work_groups: 
            log = get_object_or_404(WfWeldLog, id=log_id)
            template = 'workflow/cut_bend_weld_log/order.html'
            if request.user == log.user or log.user is None:

                order = WfWeldLog.objects.create(order=log.order, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'locksmith' in work_groups: 
            log = get_object_or_404(WfLocksmithLog, id=log_id)
            template = 'workflow/locksmith_log/order.html'
            if request.user == log.user or log.user is None:

                order = WfLocksmithLog.objects.create(order=log.order, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')
        else:
            pass
        
        order.notes_count = order.notes.count()
        order.username = request.user.username
        order.stage_id = stage_id
        current_stage = ["іав"] # list(annotate_current_stage().filter(id=log.order.id).values_list('current_stage', flat=True))
        order.current_stage = current_stage[0]

    except Exception as e:
        raise Exception(e)
    
    return render(request, template, { 'order': order })
