from django.db.models import Q, Exists, OuterRef, Subquery, Case, When, Value, Max, TextField, IntegerField, F, Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, UpdateView, DetailView, CreateView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse

from .models.core import WfOrderLog, WfOrderWorkStage, WfWorkLog, WfNoteLog
from .models.stage import WfStageList
from .forms import WfNoteLogForm
from .queries import get_max_work_stages, get_current_stage
from .utils import get_work_stage_id


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
        
        
        select_related = [
            'model', 
            'configuration', 
            'fireclay_type', 
            'glazing_type', 
            'frame_type', 
            'priority',
        ]
        
        prefetch_related = ['notes',]
        
        work_stages = get_max_work_stages()
                                           
        queryset = queryset.annotate(current_stage=Case(
                                                        When(
                                                            Exists(WfOrderWorkStage.objects.filter(Q(order=OuterRef('id')))), 
                                                            then=Subquery(work_stages.values('work_stage__stage__description'))
                                                            ),
                                                        default=Value('Очікує виконання'),
                                                        output_field=TextField()
                                                    )
                                    )
        
        if 'lead' in principal_groups:
            filter_arg &= (Q(start_manufacturing=True))
            
        else:
            
            work_stage_id = min(get_work_stage_id(work_groups) )     
            filter_arg &= (Q(work_stage__stage__id=work_stage_id))
            
            # TODO: use order_of_execution to check if its a first stage instead of work_stage_id
            previous_stages_done = WfOrderWorkStage.objects.raw('''
                                                                SELECT wows.id
                                                                FROM wf_order_work_stage wows  
                                                                INNER JOIN (
                                                                    SELECT wows.order_id AS order_id,
                                                                    CASE WHEN %(work_stage_id)s = 1 
                                                                         THEN wows.order_of_execution
                                                                         ELSE wows.order_of_execution - 1
                                                                         END
                                                                    AS previous_order_of_execution
                                                                    FROM wf_order_work_stage wows  
                                                                    WHERE wows.work_stage_id = %(work_stage_id)s
                                                                    GROUP BY wows.order_id
                                                                ) inner_
                                                                ON (wows.order_id  = inner_.order_id ) 
                                                                AND (wows.order_of_execution = inner_.previous_order_of_execution)
                                                                INNER JOIN wf_work_log wwl 
                                                                ON wwl.order_work_stage_id = wows.id
                                                                GROUP BY wows.order_id
                                                                HAVING 
                                                                    CASE 
                                                                    WHEN %(work_stage_id)s = 1 
                                                                    THEN 1=1 
                                                                    ELSE count(distinct wows.id) = sum(CASE WHEN wwl.stage_id = 1 THEN 1 ELSE 0 END) 
                                                                    END;
                                                            ''', { 'work_stage_id': work_stage_id })  
            
            previous_stages_done = [id.id for id in previous_stages_done]
            
            max_ids = WfWorkLog.objects.values('work_stage__order') \
                                       .annotate(max_id=Max('id')) \
                                       .filter(filter_arg)
            
            work_log = WfWorkLog.objects.filter(
                                            Q(id__in=max_ids.values('max_id')) & 
                                            Q(work_stage__order=OuterRef('id'))
                                        ) \
                                        .annotate(
                                            username_=F('user__username'),
                                            stage_=F('stage__id')
                                        )
            
            queryset = queryset.filter(Q(start_manufacturing=True) & Q(order_stages__id__in=previous_stages_done)) \
                               .annotate(
                                    notes_count=Count('notes'),
                                    username=Subquery(work_log.values('username_')),
                                    stage_id=Subquery(work_log.values('stage_'))
                               ) \
                               .order_by('-priority__id')
                                             
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
            elif 'cut' in work_groups:
                template = 'workflow/cut_log/list.html'
            elif 'bend' in work_groups:
                template = 'workflow/bend_log/list.html'
            elif 'weld' in work_groups:
                template = 'workflow/weld_log/list.html'
            elif any(x in ['locksmith', 'locksmith_door', ] for x in work_groups):
                template = 'workflow/locksmith_log/list.html'
            elif 'paint' in work_groups:
                template = 'workflow/paint_log/list.html'
            elif 'fireclay' in work_groups:
                template = 'workflow/fireclay_log/list.html'
            elif 'glass' in work_groups:
                template = 'workflow/glass_log/list.html'
        return template


    def get_ordering(self):
        ordering = super().get_ordering()
    
        # TODO: sort by stage of a specific log, depending on user group
        return ordering
    
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        
        if not self.request.user.is_anonymous:
            try:
                work_groups = self.request.user.work_groups.all().values_list('stage__name', flat=True)
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
        order_id = self.kwargs.get('pk')
        
        work_groups = request.user.work_groups.all().values_list('stage__name', flat=True)
        
        current_stage_ = get_current_stage(order_id)
        
        current_stage = list(current_stage_.values_list('current_stage', flat=True))[0]
        
        # allow editing order prior to glassing
        if 'dxf_version_control' in work_groups and current_stage < 9:
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
    work_groups = request.user.work_groups.all().values_list('stage__name', flat=True)
    work_stage_id = get_work_stage_id(work_groups)     
    
    template = 'workflow/order/order.html'
    create_obj = { 'user': request.user, 'stage': stage }
    order = get_object_or_404(WfOrderLog, id=order_id)
        
    try:
        
        work_stage = WfOrderWorkStage.objects.get(Q(order=order_id) & Q(stage=work_stage_id))
        
        if 'dxf_version_control' in work_groups: 
            template = 'workflow/dxf_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                WfWorkLog.objects.create(work_stage=work_stage, **create_obj)
            
            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'cut' in work_groups: 
            template = 'workflow/cut_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'bend' in work_groups: 
            template = 'workflow/bend_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')    
            
        elif 'weld' in work_groups: 
            template = 'workflow/weld_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                 WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'locksmith' in work_groups: 
            template = 'workflow/locksmith_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                 WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'locksmith_door' in work_groups: 
            template = 'workflow/locksmith_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                 WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')
        
        elif 'paint' in work_groups: 
            template = 'workflow/paint_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                 WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        elif 'fireclay' in work_groups: 
            template = 'workflow/fireclay_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                 WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')

        elif 'glass' in work_groups: 
            template = 'workflow/glass_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                 WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')

        elif 'quality_control' in work_groups: 
            template = 'workflow/dxf_log/order.html'
            
            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                 WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')
            
        else:
            pass
        
        order.notes_count = order.notes.count()
        order.username = request.user.username
        order.stage_id = stage_id
        
        work_stages = get_max_work_stages()
        
        current_stage_ = WfOrderLog.objects.annotate(current_stage=Case(
                                                        When(
                                                            Exists(WfOrderWorkStage.objects.filter(Q(order=order_id))), 
                                                            then=Subquery(work_stages.values('work_stage__stage__description'))
                                                            ),
                                                        default=Value('Очікує виконання'),
                                                        output_field=TextField()
                                                    )
                                           ) \
                                           .filter(id=order_id)
        
        order.current_stage = list(current_stage_.values_list('current_stage', flat=True))[0]

    except Exception as e:
        raise Exception(e)
    
    return render(request, template, { 'order': order })
