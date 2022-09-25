import json

from django.db.models import Q, OuterRef, Subquery, Value, Max, F, Count, Prefetch, Case, When, Exists, BooleanField
from django.db.models.lookups import GreaterThan
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, UpdateView, DetailView, CreateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, Http404
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from .models.core import Order, OrderStatus, OrderWorkStage, WorkLog, Note, WfModelList, WfWorkStageList
from .models.stage import WfStageList, OrderStatusList
from .filters import OrderFilter, NoteFilter
from .forms import OrderForm, NoteLogForm, ModelForm
from .mixins import FilteredListViewMixin
from .queries import get_max_work_stages, get_current_stage
from .utils import annotate_current_stage, annotate_notes


class OrderListView(LoginRequiredMixin, FilteredListViewMixin):

    http_method_names = ['get', 'head', 'options', 'trace',]

    queryset = Order.objects.all()
    ordering = ['-id',]
    paginate_by = 100
    filterset_class = OrderFilter

    context_object_name = 'orders'
    template_name = 'workflow/order/list.html'

    # def get_paginate_by(self, queryset):
    #     if any(x in ['manager', 'lead', ] for x in self.kwargs.get('principal_groups', [])):
    #         return 100
    #     return super().get_paginate_by(queryset)


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
            select_related += ['payment']

            ready_for_second_stage = OrderWorkStage.objects.raw(
                '''
                    SELECT * FROM wf_order_log wol
                    WHERE wol.start_manufacturing_semi_finished  = 0 AND
                    wol.id IN (
                        SELECT wows.order_id FROM wf_order_work_stage wows
                        INNER JOIN wf_work_log wwl
                        ON wows.id = wwl.order_work_stage_id
                        WHERE wows.work_stage_id <= 6
                        AND wows.order_id IN (
                            SELECT wows.order_id  FROM wf_order_work_stage wows
                            INNER JOIN wf_work_log wwl
                            ON wows.id = wwl.order_work_stage_id
                            WHERE wows.work_stage_id > 6
                            GROUP BY wows.order_id
                            HAVING COUNT(DISTINCT wows.id) = SUM(CASE WHEN wwl.stage_id = 1 THEN 0 ELSE 1 END)
                        )
                        GROUP BY wows.order_id
                        HAVING COUNT(DISTINCT wows.id) = SUM(CASE WHEN wwl.stage_id = 1 THEN 1 ELSE 0 END)
                    );
                '''
            )

            orders_ = Order.objects.filter(Q(id__in=OuterRef('id')) & Q(id__in=[id.id for id in ready_for_second_stage])) \
                                   .annotate(ready_for_second_stage=Value(True))

            max_status_ = OrderStatus.objects.values('order').annotate(max_id=Max('id'))
            is_ready = OrderStatus.objects.filter(Q(id__in=max_status_.values('max_id')) & Q(order__id=OuterRef('id')) & Q(status=2))
            is_not_cancellable = OrderStatus.objects.filter(Q(id__in=max_status_.values('max_id')) & Q(order__id=OuterRef('id')) & Q(status_id__in=[3, 4]))

            queryset = queryset.annotate(
                notes_count=Count('notes', distinct=True),
                ready_for_second_stage=Subquery(orders_.values('ready_for_second_stage')),
                ready_for_delivery=Case(
                        When(
                            Exists(is_ready) & ~Exists(OrderWorkStage.objects.filter(Q(order__id=OuterRef('id')) & Q(stage__id=12))),
                            then=Value(True)
                            ),
                        default=Value(False),
                        output_field=BooleanField()
                    ),
                is_cancellable=Case(
                        When(
                            Exists(is_not_cancellable),
                            then=Value(False)
                            ),
                        default=Value(True),
                        output_field=BooleanField()
                )
            )

        else:
            slug = self.kwargs.get('slug', None)

            try:
                stage = WfWorkStageList.objects.get(slug=slug)
            except ObjectDoesNotExist:
                raise Http404

            prefetch_related += ['notes',]

            # work_log_ = WorkLog.objects.raw(
            #     '''
            #         SELECT wwl.id
            #         FROM wf_work_log wwl
            #         INNER JOIN  (
            #             SELECT MAX(wwl_.id) AS max_id
            #             FROM wf_work_log wwl_
            #             INNER JOIN wf_order_work_stage wows_ ON wwl_.order_work_stage_id = wows_.id
            #             WHERE wows_.work_stage_id = %s
            #             GROUP BY wwl_.order_work_stage_id
            #         ) temp_
            #         ON temp_.max_id = wwl.id;
            #     ''', [stage.id]
            # )

            # work_log = WorkLog.objects.filter(
            #     Q(work_stage__order=OuterRef('id')) &
            #     Q(id__in=[id.id for id in work_log_])
            # )

            work_log_ = WorkLog.objects.values('work_stage').filter(
                            Q(work_stage__stage=stage)
                        ).annotate(max_id=Max('id'))

            work_log = WorkLog.objects.filter(
                Q(work_stage__order=OuterRef('id')) &
                Q(id__in=Subquery(work_log_.values('max_id')))
            )

            work_stage_last = OrderWorkStage.objects.values('order').filter(
                Q(order_of_execution__in=Subquery(
                    OrderWorkStage.objects.filter(Q(order=OuterRef('order')) & Q(stage=stage) & Q(is_locked=False)).values('order_of_execution')) - 1
                  ) &
                Q(order=OuterRef('id')) &
                Q(logs__stage__isnull=False)
            ).annotate(last_date=Max('logs__created_at'))


            max_status_ = OrderStatus.objects.values('order').annotate(max_id=Max('id'))
            is_delivered_or_cancelled = OrderStatus.objects.filter(Q(id__in=max_status_.values('max_id')) & Q(order__id=OuterRef('id')) & Q(status__in=[3, 4]))

            queryset = queryset.filter(
                                    Q(order_stages__stage=stage) &
                                    Q(order_stages__is_locked=False) &
                                    Q(start_manufacturing_semi_finished=Case(
                                            When(order_stages__stage__gt=6, then=True),
                                            default=F('start_manufacturing_semi_finished')
                                        )
                                    ) &
                                    ~Q(statuses__in=Subquery(is_delivered_or_cancelled.values('id')))
                                ) \
                                .annotate(
                                    notes_count=Count('notes', distinct=True),
                                    username=work_log.values('user__username'),
                                    stage_id=work_log.values('stage__id'),
                                    work_completed_date=Case(
                                        When(GreaterThan(F('order_stages__order_of_execution'), 0),
                                        then=Subquery(work_stage_last.values('last_date'))),
                                        default=F('start_date')
                                    )
                                )

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


    def dispatch(self, *args, **kwargs):
        work_groups = self.kwargs.get('work_groups', [])
        if len(work_groups) > 0 and not self.kwargs.get('slug', None):
            return redirect('workflow:orders', slug=self.request.user.work_groups.all().first().stage.slug)
        return super().dispatch(*args, **kwargs)



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
            'payment',
        ]

        work_log = WorkLog.objects.values('work_stage').filter(
            Q(work_stage=OuterRef('id'))
        ).annotate(max_id=Max('id'))

        order_stages = OrderWorkStage.objects.filter(
            Q(id=OuterRef('id')) &
            Q(is_locked=False) &
            Q(logs__id__in=Subquery(work_log.values('max_id'))) &
            Q(logs__stage__id=1) &
            Q(logs__status__id=1)
        )

        prefetch_related = [
            'notes',
            'work_stages',
            'statuses__status',
            Prefetch(
                'order_stages',
                OrderWorkStage.objects.annotate(
                                        is_done=Case(
                                            When(
                                                Exists(order_stages),
                                                then=True
                                                ),
                                            default=False,
                                            output_field=BooleanField()
                                        )
                                    ).select_related('stage')
                                     .prefetch_related('logs__user', 'logs__stage', 'logs__status').order_by('order_of_execution')
                ),
        ]

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

        principal_groups = self.request.user.groups.all().values_list('name', flat=True)

        current_stage_ = get_current_stage(self.kwargs.get('pk'))
        current_stage = list(current_stage_.values_list('current_stage', flat=True))[0]

        # disable all fields initially for security reasons
        if not any(x in ['manager', 'lead', ] for x in principal_groups):
            for field_ in list(form.fields):
                form.fields[field_].disabled = True


        for field_ in list(form.fields):
            if current_stage is None:
                # TODO: find current stage accurrately
                form.fields[field_].disabled = True
            else:
                if field_ in ['work_stages',] and current_stage == 0:
                    form.fields[field_].disabled = False
                elif field_ in ['work_stages',] and current_stage > 0:
                    form.fields[field_].disabled = True
                elif field_ in ['model', 'configuration',] and current_stage > 0:
                    form.fields[field_].disabled = True
                else:
                    pass

        # allow editing order prior to glassing
        # TODO: what logics should be here instead?
        if 'engineer' in principal_groups:
            for field_ in list(form.fields):
                if field_ in ['dxf_version', 'serial_number',]:
                    form.fields[field_].disabled = False
                if field_ in ['model', 'configuration',]:
                    form.fields[field_].disabled = True
                    if current_stage <= 1:
                        form.fields[field_].disabled = False

                if field_ in ['priority', 'deadline_date',]:
                    form.fields[field_].disabled = True
                    if current_stage < 9:
                        form.fields[field_].disabled = False

        return form



class OrderCreateView(PermissionRequiredMixin, CreateView):

    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'trace']

    permission_required = ('workflow.view_wforderlog', 'workflow.add_wforderlog',)

    model = Order
    form_class = OrderForm

    template_name = 'workflow/order_add.html'
    success_url = '/orders/'

    def get_initial(self):
        initial = super().get_initial()
        initial['work_stages'] = WfWorkStageList.objects.filter(~Q(name='locksmith_door'))
        return initial



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
    template_name = 'workflow/note/list.html'

    queryset = Note.objects.all()
    filterset_class = NoteFilter

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

    if order.order_stages.exists():
        try:
            order.start_manufacturing = True
            order.order_stages.all().filter(order_of_execution=0).update(is_locked=0)
            order.save()
        except Exception as e:
            return HttpResponse(status=400, headers={'HX-Trigger': json.dumps({
                'showMessage': {
                    'message': e,
                    'type': 'error'
                    }
                })
            })

        template = 'workflow/manager_log/order.html'

        order.notes_count = order.notes.distinct().count()
        order.current_stage='Очікує виконання'
        order.is_cancellable = True

        response = render(request, template, { 'order': order })
        response['HX-Trigger'] = json.dumps({
                'showMessage':{
                'message': 'Замовлення %s передано в роботу!' % order_id,
                'type': 'success'
            }
        })
        return response
    else:
        error_msg = 'Перед подачею замовлення %s в роботу, задайте стадії виконання.' % order_id
        return HttpResponse(status=400, headers={'HX-Trigger': json.dumps({
            'showMessage': {
                'message': error_msg,
                'type': 'error'
                }
            })
        })



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
    OrderStatus.objects.create(order=order, status=OrderStatusList.objects.get(id=4))

    try:
        response = render(request, 'workflow/empty_order.html', { 'order': None })
        response['HX-Trigger'] = json.dumps({
                'showMessage':{
                    'message': 'Замовлення %s скасовано!' % order_id,
                    'type': 'success'
                }
        })
        return response

    except Exception as e:
        return HttpResponse(status=400, headers={'HX-Trigger': json.dumps({
            'showMessage': {
                'message': e,
                'type': 'error'
                }
            })
        })


@login_required
@require_http_methods(['POST'])
def add_delivery_job(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    template = 'workflow/manager_log/order.html'

    try:
        max_order_of_execution = OrderWorkStage.objects.filter(order=order).aggregate(Max('order_of_execution'))['order_of_execution__max']
        OrderWorkStage.objects.get_or_create(order=order,
                                             stage=WfWorkStageList.objects.get(id=12),
                                             defaults={
                                                'order_of_execution': max_order_of_execution + 1,
                                                'is_locked': 0
                                                }
                                             )

        work_stages = get_max_work_stages()

        current_stage_ = Order.objects.annotate(**annotate_current_stage(work_stages)) \
                                           .filter(id=order.id)

        order.current_stage = list(current_stage_.values_list('current_stage', flat=True))[0]
        order.notes_count = order.notes.distinct().count()
        order.ready_for_delivery = False
        order.is_cancellable = True

        response = render(request, template, { 'order': order })
        response['HX-Trigger'] = json.dumps({
                'showMessage':{
                'message': 'Замовлення %s передано у відправку!' % order_id,
                'type': 'success'
            }
        })
        return response

    except Exception as e:
        return HttpResponse(status=400, headers={'HX-Trigger': json.dumps({
            'showMessage': {
                'message': e,
                'type': 'error'
                }
            })
        })


@login_required
def add_note(request, order_id):
    if request.method == "POST":
        form = NoteLogForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.order = Order.objects.get(id=order_id)
            form.save()
            return HttpResponse(status=201, headers={'HX-Trigger': 'notesListChanged'})
    else:
        form = NoteLogForm()
    return render(request, 'workflow/note/create_form.html', { 'form': form, 'order_id': order_id })


@login_required
@require_http_methods(['POST'])
def switch_job(request, slug, order_id, stage_id):

    stage = WfStageList.objects.get(id=stage_id)
    work_stage_ = get_object_or_404(WfWorkStageList, slug=slug)
    work_groups = request.user.work_groups.all().values_list('stage__name', flat=True)

    template = 'workflow/order/order.html'
    create_obj = { 'user': request.user, 'stage': stage }

    order = get_object_or_404(Order, id=order_id)

    try:
        work_stage = get_object_or_404(OrderWorkStage, order=order, stage=work_stage_, is_locked=False)
    except Exception as e:
        error_msg = 'Стадія не доступна для роботи. Зверніться до адміністратора.'
        return HttpResponse(status=400, headers={'HX-Trigger': json.dumps({
            'showMessage': {
                'message': error_msg,
                'type': 'error'
                }
            })
        })

    simultaneous_stages = OrderWorkStage.objects.filter(
        Q(order=order) &
        Q(order_of_execution=work_stage.order_of_execution)
    )
    simultaneous_stages_nr = simultaneous_stages.count()
    next_stage = OrderWorkStage.objects.filter(Q(order=order) & Q(order_of_execution=work_stage.order_of_execution + 1))

    try:

        if 'dxf_version_control' in work_groups:
            template = 'workflow/dxf_log/order.html'

        elif 'cut' in work_groups:
            template = 'workflow/cut_log/order.html'

        elif 'bend' in work_groups:
            template = 'workflow/bend_log/order.html'

        elif 'weld' in work_groups:
            template = 'workflow/weld_log/order.html'

        elif 'locksmith' in work_groups:
            template = 'workflow/locksmith_log/order.html'

        elif 'locksmith_door' in work_groups:
            template = 'workflow/locksmith_log/order.html'

        elif 'paint' in work_groups:
            template = 'workflow/paint_log/order.html'

        elif 'fireclay' in work_groups:
            template = 'workflow/fireclay_log/order.html'

        elif 'glass' in work_groups:
            template = 'workflow/glass_log/order.html'

        elif 'quality_control' in work_groups:
            template = 'workflow/dxf_log/order.html'

        elif 'final_product' in work_groups:
            template = 'workflow/final_product_log/order.html'

        else:
            pass

        last_user = work_stage.logs.all().order_by('-created_at').first().user

        if request.user == last_user or last_user is None:
            WorkLog.objects.get_or_create(work_stage=work_stage, **create_obj)
        else:
            raise Exception('The user is allowed to edit only his entries!')

        if stage_id == 1:

            if simultaneous_stages_nr > 1:

                work_log = WorkLog.objects.values('work_stage').filter(
                    Q(work_stage__in = simultaneous_stages.values('id')) &
                    Q(stage=1)
                )
                if simultaneous_stages_nr == work_log.count():
                    if next_stage.exists():
                        next_stage.update(is_locked=False)
                    else:
                        OrderStatus.objects.get_or_create(order=order, status=OrderStatusList.objects.get(id=2))
            else:
                if next_stage.exists():
                    next_stage.update(is_locked=False)
                else:
                    if work_stage.stage.id == 12:
                        status = OrderStatusList.objects.get(id=3)
                    else:
                        status = OrderStatusList.objects.get(id=2)
                    OrderStatus.objects.get_or_create(order=order, status=status)

        order.notes_count = order.notes.distinct().count()
        order.username = request.user.username
        order.stage_id = stage_id

        work_stages = get_max_work_stages()

        current_stage_ = Order.objects.annotate(**annotate_current_stage(work_stages)) \
                                           .filter(id=order.id)

        order.current_stage = list(current_stage_.values_list('current_stage', flat=True))[0]

        max_order_of_execution = OrderWorkStage.objects.values('order') \
                                            .filter(
                                                Q(stage__assignees__user=request.user) &
                                                Q(is_locked=False)
                                                ) \
                                            .annotate(max_order=Max('order_of_execution'))

        work_stage_last = OrderWorkStage.objects.values('order').filter(
            Q(order_of_execution__in=Subquery(
                max_order_of_execution.filter(Q(order=order)).values('max_order')) - 1
                ) &
            Q(order=order) &
            Q(logs__stage__isnull=False)
        ).annotate(last_date=Max('logs__created_at'))

        try:
            if work_stage.order_of_execution > 0:
                work_completed_date = list(work_stage_last.values_list('last_date', flat=True))[0]
            else:
                work_completed_date = order.start_date
            order.work_completed_date = work_completed_date
        except:
            pass

        message = json.dumps({
            'showMessage':{
            'message': 'Зміни збережено!',
            'type': 'success'
            }
        })

    except Exception as e:
        message = json.dumps({
                'showMessage':{
                'message': 'Цей-во, помилка на сервері: "%s"' % e,
                'type': 'error'
            }
        })

    response = render(request, template, { 'order': order })
    response['HX-Trigger'] = message

    return response
