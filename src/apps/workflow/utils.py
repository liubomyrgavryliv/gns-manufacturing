from django.db.models import Q, Max, OuterRef, Exists
from django.core.exceptions import PermissionDenied

from .models.core import WfWorkLog


def get_previous_current_stage_id(work_groups):
    
    if 'dxf_version_control' in work_groups:
        return 1, None

    elif 'cut' in work_groups:
                                                               
        return 2, 1
        
    elif 'bend' in work_groups:
        return 3, 2
        
    elif 'weld' in work_groups:
        return 1, None
        
    elif 'locksmith' in work_groups:
        return 1, None
    else:
        raise PermissionDenied
        
    return 1, None


def get_work_group_filter_arg(work_groups):
    filter_arg = Q()
    if 'dxf_version_control' in work_groups:
        filter_arg &= (Q(work_stage__stage__id=1))

    elif 'cut' in work_groups:
                                                               
        filter_arg &= (Q(work_stage__stage__id=2))
        
    elif 'bend' in work_groups:
        filter_arg &= (Q(work_stage__stage__id=3))
        
    elif 'weld' in work_groups:
        filter_arg &= (Q(work_stage__stage__id=4))
        
    elif 'locksmith' in work_groups:
        filter_arg &= (Q(work_stage__stage__id=5))
    else:
        raise PermissionDenied
        
    return filter_arg
