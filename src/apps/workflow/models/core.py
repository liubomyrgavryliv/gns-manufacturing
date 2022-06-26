import datetime

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.contrib import admin
from django.utils.html import format_html

from .base import BaseModel, Nameable, Creatable
from .stage import WfStageList, WfStageFinalList, WfWorkStageList


class WfModelList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_model_list'
        
        verbose_name = 'Модель Топки'
        verbose_name_plural = 'Моделі Топок'


    def __str__(self):
        return self.name



class WfJobStatusList(BaseModel, Nameable):
    
    DEFAULT_STATUS_ID = 1

    class Meta:
        managed = False
        db_table = 'wf_job_status_list'
        
        verbose_name = 'Статус виконання робіт'
        verbose_name_plural = 'Статуси виконання робіт'


    def __str__(self):
        return self.name
    
    

class WfConfigurationList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_configuration_list'
        
        verbose_name = 'Конфігурацію Топки'
        verbose_name_plural = 'Конфігурації Топок'


    def __str__(self):
        return self.name



class WfFireclayTypeList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_fireclay_type_list'
        
        verbose_name = 'Тип шамотування'
        verbose_name_plural = 'Типи шамотування'


    def __str__(self):
        return self.name



class WfFrameTypeList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_frame_type_list'
        
        verbose_name = 'Тип рами'
        verbose_name_plural = 'Типи рам'


    def __str__(self):
        return self.name



class WfGlazingTypeList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_glazing_type_list'
        
        verbose_name = 'Тип скління'
        verbose_name_plural = 'Типи скління'


    def __str__(self):
        return self.name



class WfPriorityList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_priority_list'
        
        verbose_name = 'Пріоритет'
        verbose_name_plural = 'Пріоритети'


    def __str__(self):
        return self.name



class WfPaymentList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_payment_list'
        
        verbose_name = 'Тип олати'
        verbose_name_plural = 'Типи оплати'


    def __str__(self):
        return self.name
    
    
    
class WfAuthUserGroup(BaseModel):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True, related_name='work_groups')
    stage = models.ForeignKey(WfWorkStageList, on_delete=models.SET_NULL, db_column='work_stage_id', null=True)

    class Meta:
        managed = False
        db_table = 'wf_auth_user_group'
        
        verbose_name = 'Сферу працівників'
        verbose_name_plural = 'Сфери працівників'


    def __str__(self):
        return str(self.id)



class WfNoteLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id', related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    note = models.TextField(null=True, blank=False)
    

    class Meta:
        managed = False
        db_table = 'wf_note_log'
        
        verbose_name = 'Лог нотатки'
        verbose_name_plural = 'Логи нотаток'

    def __str__(self):
        return self.id
    


class WfOrderLog(BaseModel, Creatable):

    model = models.ForeignKey(WfModelList, on_delete=models.CASCADE, db_column='model_id')
    configuration = models.ForeignKey(WfConfigurationList, on_delete=models.CASCADE, db_column='configuration_id')
    fireclay_type = models.ForeignKey(WfFireclayTypeList, on_delete=models.CASCADE, db_column='fireclay_type_id')
    glazing_type = models.ForeignKey(WfGlazingTypeList, on_delete=models.CASCADE, db_column='glazing_type_id')
    frame_type = models.ForeignKey(WfFrameTypeList, on_delete=models.CASCADE, db_column='frame_type_id')
    priority = models.ForeignKey(WfPriorityList, on_delete=models.CASCADE, db_column='priority_id')

    delivery = models.TextField(null=True, blank=True)
    mobile_number = models.TextField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    payment = models.ForeignKey(WfPaymentList, on_delete=models.CASCADE, db_column='payment_id')

    start_manufacturing = models.BooleanField(default=False)

    start_date = models.DateTimeField(null=True, blank=True)
    deadline_date = models.DateTimeField(null=True, blank=True)
    
    work_stages = models.ManyToManyField('workflow.WfWorkStageList', through='WfOrderWorkStage')

    class Meta:
        managed = False
        db_table = 'wf_order_log'
        ordering = ['-created_at']
        
        verbose_name = 'Лог Замовлень'
        verbose_name_plural = 'Логи Замовлень'
    
    def current_stage(self):
        return 'DXF'
        
    
    @admin.display(description='Priority')
    def _priority(self):
        color = 'green'
        if self.priority.name == 'високий':
            color = 'red'
        elif self.priority.name == 'середній':
            color = 'orange'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, 
            self.priority,
        )


    @admin.display(description='Start Date')
    def _start_date(self):
        return naturaltime(self.start_date)
    
    
    @admin.display(description='Semi-finished product ready for passing?', boolean=True)
    def semifinished_ready(self):
        if hasattr(self, 'semifinished_ready_'):
            return self.semifinished_ready_
        return None 
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.start_manufacturing:
            work_stages = WfOrderWorkStage.objects.filter(Q(order=self))
            
            if not work_stages.exists():
                normal_work_stages = WfWorkStageList.objects.all().order_by('id')
                WfOrderWorkStage.objects.bulk_create([
                    WfOrderWorkStage(order=self, stage=normal_work_stages[0], order_of_execution=0),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[1], order_of_execution=1),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[2], order_of_execution=2),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[3], order_of_execution=3),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[4], order_of_execution=3),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[5], order_of_execution=3),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[6], order_of_execution=4),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[7], order_of_execution=5),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[8], order_of_execution=5),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[9], order_of_execution=6),
                    WfOrderWorkStage(order=self, stage=normal_work_stages[10], order_of_execution=7),
                ])
                
            for work_stage in WfOrderWorkStage.objects.filter(Q(order=self)):
                WfWorkLog.objects.create(work_stage=work_stage, stage=None)
            if not self.start_date:
                self.start_date = datetime.datetime.now()
                
                
    def __str__(self):
        return str(self.id)


    def get_absolute_url(self):
        return reverse('workflow:order-detail', kwargs={'pk': self.pk})



class WfOrderWorkStage(BaseModel):

    order = models.ForeignKey(WfOrderLog, on_delete=models.CASCADE, db_column='order_id', related_name='order_stages')
    stage = models.ForeignKey(WfWorkStageList, on_delete=models.RESTRICT, db_column='work_stage_id', null=True)
    order_of_execution = models.IntegerField(null=True)
    

    class Meta:
        managed = False
        db_table = 'wf_order_work_stage'
        
        verbose_name = 'Стадія замовлення'
        verbose_name_plural = 'Стадії замовлення'

    def __str__(self):
        return str(self.id)
    
    
    
class WfWorkLog(BaseModel, Creatable):

    work_stage = models.ForeignKey(WfOrderWorkStage, on_delete=models.RESTRICT, db_column='order_work_stage_id', related_name='logs')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id', default=WfStageList.DEFAULT_STAGE_ID)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID)


    class Meta:
        managed = False
        db_table = 'wf_work_log'
        
        verbose_name = 'Лог виробництва'
        verbose_name_plural = 'Логи виробництва'


    def __str__(self):
        return str(self.id)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
