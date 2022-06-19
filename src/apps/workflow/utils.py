from django.core.exceptions import PermissionDenied


def get_work_stage_id(work_groups):
    
    if 'dxf_version_control' in work_groups:
        return 1

    elif 'cut' in work_groups:                                             
        return 2
        
    elif 'bend' in work_groups:
        return 3
        
    elif 'weld' in work_groups:
        return 4
        
    elif 'locksmith' in work_groups:
        return 5
    
    elif 'locksmith_door' in work_groups:
        return 6
    
    elif 'paint' in work_groups:
        return 7

    elif 'fireclay' in work_groups:
        return 8

    elif 'glass' in work_groups:
        return 9
    
    elif 'quality_control' in work_groups:
        return 10
    
    elif 'final_product' in work_groups:
        return 11
    
    else:
        raise PermissionDenied
