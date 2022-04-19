from .base import BaseModel, Nameable


class WfStageList(BaseModel, Nameable):
    
    DEFAULT_STAGE_ID = 2

    class Meta:
        managed = False
        db_table = 'wf_stage_list'


    def __str__(self):
        return self.name



class WfStageSemiFinishedList(BaseModel, Nameable):
    
    DEFAULT_STAGE_ID = 2

    class Meta:
        managed = False
        db_table = 'wf_stage_semi_finished_list'


    def __str__(self):
        return self.name



class WfStageFinalList(BaseModel, Nameable):
    
    DEFAULT_STAGE_ID = 1

    class Meta:
        managed = False
        db_table = 'wf_stage_final_list'


    def __str__(self):
        return self.name