from django.db.models import Q, OuterRef, Max

from .models.core import WfWorkLog


def get_max_work_stages():
    
      max_id_per_order = WfWorkLog.objects.values('work_stage__order').annotate(max_id=Max('id'))
      work_stages = WfWorkLog.objects.filter(Q(id__in=max_id_per_order.values('max_id')) & (Q(work_stage__order__id=OuterRef('id'))) & Q(stage__isnull=False))
      
      return work_stages                                    
