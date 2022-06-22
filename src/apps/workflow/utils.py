from django.core.exceptions import PermissionDenied


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
