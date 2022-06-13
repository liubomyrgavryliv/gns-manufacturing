from django.db import models

from .base import BaseModel, Nameable


class WfStageList(BaseModel, Nameable):
    
    DEFAULT_STAGE_ID = 2

    class Meta:
        managed = False
        db_table = 'wf_stage_list'


    def __str__(self):
        return self.name
    


class WfStageFinalList(BaseModel, Nameable):
    
    DEFAULT_STAGE_ID = 1

    class Meta:
        managed = False
        db_table = 'wf_stage_final_list'


    def __str__(self):
        return self.name
    
    
    
class WfWorkStageList(BaseModel, Nameable):
    
    description = models.TextField(blank=True, null=True)
    
    DEFAULT_STAGE_ID = 1

    class Meta:
        managed = False
        db_table = 'wf_work_stage_list'


    def __str__(self):
        return self.name
