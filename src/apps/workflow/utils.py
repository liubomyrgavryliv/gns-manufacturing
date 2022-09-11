from django.db.models import Q, Case, Count, When, Exists, Subquery, F, Value, TextField, OuterRef, Max

from .models.core import OrderWorkStage, OrderStatus


def get_work_stage_id(work_groups):

    work_stage_ids = []

    if 'dxf_version_control' in work_groups:
        work_stage_ids.append(1)

    if 'cut' in work_groups:
        work_stage_ids.append(2)

    if 'bend' in work_groups:
        work_stage_ids.append(3)

    if 'weld' in work_groups:
        work_stage_ids.append(4)

    if 'locksmith' in work_groups:
        work_stage_ids.append(5)

    if 'locksmith_door' in work_groups:
        work_stage_ids.append(6)

    if 'paint' in work_groups:
        work_stage_ids.append(7)

    if 'fireclay' in work_groups:
        work_stage_ids.append(8)

    if 'glass' in work_groups:
        work_stage_ids.append(9)

    if 'quality_control' in work_groups:
        work_stage_ids.append(10)

    if 'final_product' in work_groups:
        work_stage_ids.append(11)

    return work_stage_ids


def annotate_current_stage(work_stages):

    max_status_ = OrderStatus.objects.values('order').annotate(max_id=Max('id'))
    max_status = OrderStatus.objects.filter(Q(id__in=max_status_.values('max_id')) & (Q(order__id=OuterRef('id'))))

    return { 'current_stage': Case(
                                    # When(is_finished=True, then=Value('Виготовлено')),
                                    When(
                                        Exists(OrderStatus.objects.filter(Q(order=OuterRef('id')) & Q(status__gt=1))),
                                        then=Subquery(max_status.values('status__name'))
                                        ),
                                    When(
                                        Exists(OrderWorkStage.objects.filter(Q(order=OuterRef('id')) & Q(logs__stage__isnull=False))),
                                        then=Subquery(work_stages.values('work_stage__stage__description'))
                                        ),
                                    default=Value('Очікує виконання'),
                                    output_field=TextField()
                                )
            }


def annotate_notes():
    return { 'notes_count': Count('notes', distinct=True) }
