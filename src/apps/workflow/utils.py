from django.db.models import Q, Case, Count, When, Exists, Subquery, Value, TextField, OuterRef, Max

from .models.core import OrderWorkStage, OrderStatus


def annotate_current_stage(work_stages):

    max_status_ = OrderStatus.objects.values('order').annotate(max_id=Max('id'))
    max_status = OrderStatus.objects.filter(Q(id__in=max_status_.values('max_id')) & (Q(order__id=OuterRef('id'))))

    return { 'current_stage': Case(
                                    When(
                                        Exists(OrderStatus.objects.filter(Q(order=OuterRef('id')) & Q(status__gt=2))),
                                        then=Subquery(max_status.values('status__name'))
                                        ),
                                    When(
                                        Exists(OrderStatus.objects.filter(Q(order=OuterRef('id')) & Q(status=2))) &
                                        Exists(OrderWorkStage.objects.filter(Q(order=OuterRef('id')) & Q(stage__id=12))),
                                        then=Subquery(work_stages.values('work_stage__stage__description'))
                                        ),
                                    When(
                                        Exists(OrderWorkStage.objects.filter(Q(order=OuterRef('id')) & Q(logs__stage__isnull=False))),
                                        then=Subquery(work_stages.values('work_stage__stage__description'))
                                        ),
                                    default=Value('Очікує виконання'),
                                    output_field=TextField()
                                ),
            }


def annotate_notes():
    return { 'notes_count': Count('notes', distinct=True) }
