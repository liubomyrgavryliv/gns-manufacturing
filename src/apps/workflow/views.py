import json

from django.db.models import Q, OuterRef, Subquery, Value, Max, F, Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, UpdateView, DetailView, CreateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse

from .models.core import Order, WfOrderWorkStage, WfWorkLog, WfNoteLog, WfModelList
from .models.stage import WfStageList
from .filters import OrderFilter
from .forms import OrderForm, WfNoteLogForm, ModelForm
from .mixins import FilteredListViewMixin
from .queries import get_max_work_stages, get_current_stage
from .utils import annotate_current_stage, annotate_notes


class OrderListView(LoginRequiredMixin, FilteredListViewMixin):

    http_method_names = ['get', 'head', 'options', 'trace',]

    queryset = Order.objects.all()
    ordering = ['-priority', '-start_date', 'deadline_date',]
    paginate_by = 10
    filterset_class = OrderFilter

    context_object_name = 'orders'
    template_name = 'workflow/order/list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        principal_groups = self.kwargs.get('principal_groups', [])

        select_related = [
            'model',
            'configuration',
            'fireclay_type',
            'glazing_type',
            'frame_type',
            'priority',
        ]

        prefetch_related = []

        work_stages = get_max_work_stages()

        queryset = queryset.annotate(**annotate_current_stage(work_stages))

        if any(x in ['manager', 'lead', ] for x in principal_groups):
            # TODO: calculate status field
            select_related += ['payment']

            ready_for_second_stage = WfOrderWorkStage.objects.raw(
                '''
                    SELECT wows.* FROM wf_order_work_stage wows
                    INNER JOIN wf_order_log wol ON wol.id = wows.order_id
                    INNER JOIN wf_work_log wwl ON wwl.order_work_stage_id = wows.id
                    WHERE (
                        wol.start_manufacturing_semi_finished = FALSE AND
                        wows.id IN (
                            SELECT wows.id FROM wf_order_work_stage wows
                            WHERE wows.work_stage_id <= 6
                            GROUP BY wows.order_id
                            HAVING count(wows.work_stage_id) = 6
                        )
                    )
                    GROUP BY wows.work_stage_id
                    HAVING COUNT(DISTINCT wows.id) = SUM(CASE WHEN wwl.stage_id = 1 THEN 1 ELSE 0 END);
                '''
            )

            orders_ = Order.objects.filter(Q(id__in=OuterRef('id')) & Q(id__in=[id.order_id for id in ready_for_second_stage])) \
                                        .annotate(ready_for_second_stage=Value(True))

            queryset = queryset.annotate(
                status=Value('В роботі'),
                notes_count=Count('notes', distinct=True),
                ready_for_second_stage=Subquery(orders_.values('ready_for_second_stage'))
            )

        else:

            prefetch_related += ['notes',]

            previous_stages_done = WfOrderWorkStage.objects.raw(
                '''
                    SELECT wows.*  FROM
                    wf_order_work_stage wows
                    INNER JOIN (
                        SELECT wows.id AS previous_stage, inner_.next_stage_id, inner_.is_first_stage FROM wf_order_work_stage wows
                        INNER JOIN (
                            SELECT wows.id AS next_stage_id, wows.order_id, wows.order_of_execution,
                            CASE
                                WHEN wows.order_of_execution = 0 THEN TRUE
                                ELSE FALSE
                                END AS is_first_stage
                            FROM wf_order_work_stage wows
                            INNER JOIN wf_auth_user_group waug ON waug.work_stage_id = wows.work_stage_id
                            WHERE waug.user_id = %s
                        ) inner_ ON inner_.order_id = wows.order_id
                        AND wows.order_of_execution = (
                            CASE WHEN inner_.is_first_stage THEN inner_.order_of_execution ELSE inner_.order_of_execution - 1 END
                        )
                        INNER JOIN wf_work_log wwl ON wwl.order_work_stage_id = wows.id
                        GROUP BY inner_.next_stage_id
                        HAVING
                            CASE
                            WHEN inner_.is_first_stage THEN 1 = 1
                            ELSE count(distinct wows.id) = SUM(CASE WHEN wwl.stage_id = 1 THEN 1 ELSE 0 END)
                            END
                    ) temp_ ON temp_.previous_stage = wows.id
                    INNER JOIN wf_work_log wwl ON wwl.order_work_stage_id = wows.id
                    WHERE wwl.stage_id = 1;
                ''', [self.request.user.id]
            )

            previous_stage_logs = WfWorkLog.objects.values('work_stage__order') \
                                                   .annotate(
                                                       max_date=Max('created_at')
                                                    ) \
                                                   .filter(Q(work_stage__in=[id.id for id in previous_stages_done]) &
                                                           Q(stage__id=1) &
                                                           Q(work_stage__order=OuterRef('id')))

            available_stages = WfOrderWorkStage.objects.raw(
                '''
                    SELECT wows.*
                    FROM wf_order_work_stage wows
                    INNER JOIN (
                        SELECT max(wows.work_stage_id) AS work_stage_id, wows.order_id
                        FROM wf_order_work_stage wows
                        INNER JOIN  (
                            SELECT wows.id, inner_.next_stage_id, inner_.is_first_stage FROM wf_order_work_stage wows
                            INNER JOIN (
                                SELECT wows.id AS next_stage_id, wows.order_id, wows.order_of_execution,
                                CASE
                                    WHEN wows.order_of_execution = 0 THEN TRUE
                                    ELSE FALSE
                                    END AS is_first_stage
                                FROM wf_order_work_stage wows
                                INNER JOIN wf_auth_user_group waug ON waug.work_stage_id = wows.work_stage_id
                                WHERE waug.user_id = %s
                            ) inner_ ON inner_.order_id = wows.order_id
                            AND wows.order_of_execution = (
                                CASE WHEN inner_.is_first_stage THEN inner_.order_of_execution ELSE inner_.order_of_execution - 1 END
                            )
                            INNER JOIN wf_work_log wwl ON wwl.order_work_stage_id = wows.id
                            GROUP BY inner_.next_stage_id
                            HAVING
                                CASE
                                WHEN inner_.is_first_stage THEN 1 = 1
                                ELSE count(distinct wows.id) = SUM(CASE WHEN wwl.stage_id = 1 THEN 1 ELSE 0 END)
                                END
                        ) temp_ ON temp_.next_stage_id = wows.id
                        GROUP BY wows.order_id
                    ) temp_ ON temp_.order_id = wows.order_id AND temp_.work_stage_id = wows.work_stage_id
                    INNER JOIN wf_order_log wol ON wol.id = wows.order_id
                    WHERE
                        CASE
                            WHEN wows.work_stage_id > 6
                            THEN wol.start_manufacturing_semi_finished = 1
                            ELSE 1 = 1
                        END;
                ''', [self.request.user.id]
                )

            max_ids = WfWorkLog.objects.values('work_stage__order') \
                                       .annotate(max_id=Max('id')) \
                                       .filter(work_stage__in=[id.id for id in available_stages])

            work_log = WfWorkLog.objects.filter(
                                            Q(id__in=max_ids.values('max_id')) &
                                            Q(work_stage__order=OuterRef('id'))
                                        ) \
                                        .annotate(
                                            username_=F('user__username'),
                                            stage_=F('stage__id'),
                                            work_stage_=F('work_stage__id'),
                                        )

            queryset = queryset.filter(Q(start_manufacturing=True) & Q(order_stages__id__in=[id.id for id in available_stages])) \
                               .annotate(
                                    notes_count=Count('notes', distinct=True),
                                    username=Subquery(work_log.values('username_')),
                                    stage_id=Subquery(work_log.values('stage_')),
                                    order_stage_id=Subquery(work_log.values('work_stage_')),
                                    work_completed_date=Subquery(previous_stage_logs.values('max_date'))
                               ) \
                               .order_by('-priority__id')

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)

        return queryset


    def get_template_names(self):
        template = super().get_template_names()

        principal_groups = self.kwargs.get('principal_groups', [])
        work_groups = self.kwargs.get('work_groups', [])

        if any(x in ['manager', 'lead', ] for x in principal_groups):
            template = 'workflow/manager_log/list.html'

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
            elif 'final_product' in work_groups:
                template = 'workflow/final_product_log/list.html'
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
    model = Order

    template_name = 'workflow/order_detail.html'


    def get_queryset(self):
        queryset = super().get_queryset()

        select_related = [
            'model',
            'configuration',
            'fireclay_type',
            'glazing_type',
            'frame_type',
            'priority',
        ]

        prefetch_related = []

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)

        return queryset



class OrderUpdateView(PermissionRequiredMixin, UpdateView):

    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'trace']

    permission_required = ('workflow.view_wforderlog', 'workflow.change_wforderlog',)

    model = Order
    form_class = OrderForm

    template_name = 'workflow/order_update.html'
    success_url = '/orders/'

    def get_queryset(self):
        queryset = super().get_queryset()

        select_related = [
            'model',
            'configuration',
            'fireclay_type',
            'glazing_type',
            'frame_type',
            'priority',
        ]

        prefetch_related = [
            'order_stages',
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)

        return queryset


    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        work_groups = self.request.user.work_groups.all().values_list('stage__name', flat=True)
        principal_groups = self.request.user.groups.all().values_list('name', flat=True)

        current_stage_ = get_current_stage(self.kwargs.get('pk'))
        current_stage = list(current_stage_.values_list('current_stage', flat=True))[0]

        # disable all fields initially for security reasons
        if not any(x in ['manager', 'lead', ] for x in principal_groups):
            for field_ in list(form.fields):
                form.fields[field_].disabled = True


        for field_ in list(form.fields):
            if field_ in ['work_stages',] and current_stage == 0:
                form.fields[field_].disabled = False
            elif field_ in ['work_stages',] and current_stage > 0:
                form.fields[field_].disabled = True
            else:
                pass


        # allow editing order prior to glassing
        if current_stage < 9:
            if 'dxf_version_control' in work_groups:
                for field_ in list(form.fields):
                    if field_ in ['priority', 'model', 'configuration', 'deadline_date',]:
                        form.fields[field_].disabled = False
            else:
                pass

        return form



class OrderCreateView(PermissionRequiredMixin, CreateView):

    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'trace']

    permission_required = ('workflow.view_wforderlog', 'workflow.change_wforderlog',)

    model = Order
    form_class = OrderForm

    template_name = 'workflow/order_add.html'
    success_url = '/orders/'



class ModelListView(PermissionRequiredMixin, ListView):

    http_method_names = ['get', 'head', 'options', 'trace']
    permission_required = ('workflow.view_wfmodellist',)

    ordering = ['id',]

    context_object_name = 'models'

    queryset = WfModelList.objects.all()

    template_name = 'workflow/model/list.html'



class ModelUpdateView(LoginRequiredMixin, UpdateView):

    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'trace']
    permission_required = ('workflow.view_wfmodellist', 'workflow.change_wfmodellist',)

    model = WfModelList
    form_class = ModelForm

    template_name = 'workflow/model/update.html'
    success_url = '/models/'



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



@permission_required(['workflow.add_wfmodellist'])
@login_required
def add_model(request):
    if request.method == "POST":
        form = ModelForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=201, headers={'HX-Trigger': 'modelsListChanged'})
    else:
        form = ModelForm()
    return render(request, 'workflow/model/create.html', { 'form': form })



@login_required
@require_http_methods(['POST'])
def start_job(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    order.start_manufacturing = True
    order.save()

    template = 'workflow/manager_log/order.html'

    order.notes_count = order.notes.distinct().count()
    order.status='В роботі'

    return render(request, template, { 'order': order })



@login_required
@require_http_methods(['POST'])
def start_second_stage(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    template = 'workflow/manager_log/order.html'

    if order.fireclay_type and order.glazing_type and order.payment and order.frame_type:
        order.start_manufacturing_semi_finished = True
        order.save()


        work_stages = get_max_work_stages()
        order_ = Order.objects.filter(id=order.id) \
                                .annotate(
                                        **annotate_current_stage(work_stages),
                                        **annotate_notes(),
                                    )

        response = render(request, template, { 'order': order_.first() })
        response['HX-Trigger'] = json.dumps({
                'showMessage':{
                'message': 'Напівфабрикат передано в роботу!',
                'type': 'success'
            }
        })
        return response

    else:
        error_msg = 'Перед подачею напівфабрикату в роботу, задайте тип шамотування, тип рами, тип скління та оплату.'
        return HttpResponse(status=400, headers={'HX-Trigger': json.dumps({
            'showMessage': {
                'message': error_msg,
                'type': 'error'
                }
            })
                                                 })



@login_required
@require_http_methods(['DELETE'])
def cancel_job(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    order.is_canceled = True
    order.save()

    template = 'workflow/manager_log/list.html'

    queryset = Order.objects.all()

    select_related = [
        'model',
        'configuration',
        'fireclay_type',
        'glazing_type',
        'frame_type',
        'priority',
    ]

    prefetch_related = []

    work_stages = get_max_work_stages()

    queryset = queryset.filter(Q(is_canceled=False)) \
                        .annotate(
                                    **annotate_current_stage(work_stages),
                                    **annotate_notes(),
                                ) \
                        .order_by('priority', '-start_date', 'deadline_date')

    queryset.select_related(*select_related).prefetch_related(*prefetch_related)

    return render(request, template, { 'orders': queryset })


@login_required
def add_note(request, order_id):
    if request.method == "POST":
        form = WfNoteLogForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.order = Order.objects.get(id=order_id)
            form.save()
            return HttpResponse(status=201, headers={'HX-Trigger': 'notesListChanged'})
    else:
        form = WfNoteLogForm()
    return render(request, 'workflow/note/create_form.html', { 'form': form, 'order_id': order_id })


@login_required
@require_http_methods(['POST'])
def switch_job(request, order_stage_id, stage_id):

    stage = WfStageList.objects.get(id=stage_id)
    work_groups = request.user.work_groups.all().values_list('stage__name', flat=True)

    template = 'workflow/order/order.html'
    create_obj = { 'user': request.user, 'stage': stage }
    work_stage =  get_object_or_404(WfOrderWorkStage, id=order_stage_id)
    order = get_object_or_404(Order, id=work_stage.order_id)

    try:

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

        elif 'final_product' in work_groups:
            template = 'workflow/final_product_log/order.html'

            last_user = work_stage.logs.all().order_by('-created_at').first().user
            if request.user == last_user or last_user is None:

                 WfWorkLog.objects.create(work_stage=work_stage, **create_obj)

            else:
                raise Exception('The user is allowed to edit only his entries!')

        else:
            pass

        order.notes_count = order.notes.distinct().count()
        order.username = request.user.username
        order.order_stage_id = order_stage_id
        order.stage_id = stage_id

        work_stages = get_max_work_stages()

        current_stage_ = Order.objects.annotate(**annotate_current_stage(work_stages)) \
                                           .filter(id=order.id)

        order.current_stage = list(current_stage_.values_list('current_stage', flat=True))[0]

    except Exception as e:
        raise Exception(e)

    return render(request, template, { 'order': order })
