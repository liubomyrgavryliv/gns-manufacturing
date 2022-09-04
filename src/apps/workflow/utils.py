from django.db.models import Q, Case, Count, When, Exists, Subquery, Value, TextField, OuterRef

from .models.core import WfOrderWorkStage


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

    return { 'current_stage': Case(
                                    When(is_finished=True, then=Value('Виготовлено')),
                                    When(
                                        Exists(WfOrderWorkStage.objects.filter(Q(order=OuterRef('id')) & Q(logs__stage__isnull=False))),
                                        then=Subquery(work_stages.values('work_stage__stage__description'))
                                        ),
                                    default=Value('Очікує виконання'),
                                    output_field=TextField()
                                )
            }


def annotate_notes():
    return { 'notes_count': Count('notes', distinct=True) }
