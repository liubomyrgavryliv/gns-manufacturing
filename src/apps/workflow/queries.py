from django.db.models import Q, OuterRef, Max, Exists, Subquery, IntegerField, Case, When, Value

from .models.core import WfWorkLog, Order, WfOrderWorkStage


def get_max_work_stages():

      max_id_per_order = WfWorkLog.objects.values('work_stage__order').annotate(max_id=Max('id'))
      work_stages = WfWorkLog.objects.filter(Q(id__in=max_id_per_order.values('max_id')) & (Q(work_stage__order__id=OuterRef('id'))) & Q(stage__isnull=False))

      return work_stages


def get_current_stage(order_id):

      work_stages = get_max_work_stages()

      return Order.objects.annotate(current_stage=Case(
                                                        When(
                                                            Exists(WfOrderWorkStage.objects.filter(Q(order=order_id) & Q(logs__stage__isnull=False))),
                                                            then=Subquery(work_stages.values('work_stage__stage__id'))
                                                            ),
                                                        default=Value(0),
                                                        output_field=IntegerField()
                                                    )
                                           ) \
                               .filter(id=order_id)
