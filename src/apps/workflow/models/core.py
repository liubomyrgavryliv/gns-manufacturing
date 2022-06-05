import datetime

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.contrib import admin
from django.utils.html import format_html

from .base import BaseModel, Nameable, Creatable, Updatable
from .stage import WfStageList, WfStageSemiFinishedList, WfStageFinalList


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



class WfUserGroupList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_user_group_list'
        
        verbose_name = 'Групу працівників'
        verbose_name_plural = 'Групи працівників'


    def __str__(self):
        return self.name
    
    
    
class WfAuthUserGroup(BaseModel):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True, related_name='work_groups')
    group = models.ForeignKey(WfUserGroupList, on_delete=models.SET_NULL, db_column='group_id', null=True)

    class Meta:
        managed = False
        db_table = 'wf_auth_user_group'
        
        verbose_name = 'Сферу працівників'
        verbose_name_plural = 'Сфери працівників'


    def __str__(self):
        return str(self.id)
    


class WfDXFVersionControlLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id', related_name='dxf_logs')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id', default=WfStageList.DEFAULT_STAGE_ID)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID)


    class Meta:
        managed = False
        db_table = 'wf_dxf_version_control_log'
        ordering = ['created_at']
        
        verbose_name = 'Лог DXF Версії'
        verbose_name_plural = 'Логи DXF Версій'


    def __str__(self):
        return str(self.id)


    def save(self, *args, **kwargs):
        if hasattr(self, 'stage') and self.stage.id == 1:
            if not WfCutLog.objects.filter(Q(order=self.order) & Q(stage__isnull=True) & Q(user__isnull=True) & Q(status=1)).exists():
                WfCutLog.objects.create(order=self.order, stage=None)
        super().save(*args, **kwargs)



class WfCutLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id', related_name='cut_logs')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id', default=WfStageList.DEFAULT_STAGE_ID)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID)


    class Meta:
        managed = False
        db_table = 'wf_cut_log'
        
        verbose_name = 'Лог різки'
        verbose_name_plural = 'Логи різки'


    def __str__(self):
        return str(self.id)


    def save(self, *args, **kwargs):
        if hasattr(self, 'stage') and self.stage.id == 1:
            if not WfBendLog.objects.filter(Q(order=self.order) & Q(stage__isnull=True) & Q(user__isnull=True) & Q(status=1)).exists():
                WfBendLog.objects.create(order=self.order, stage=None)
        super().save(*args, **kwargs)
        


class WfBendLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id', related_name='bend_logs')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id', default=WfStageList.DEFAULT_STAGE_ID)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID)


    class Meta:
        managed = False
        db_table = 'wf_bend_log'
        
        verbose_name = 'Лог гнуття'
        verbose_name_plural = 'Логи гнуття'


    def __str__(self):
        return self.id


    def save(self, *args, **kwargs):
        if hasattr(self, 'stage') and self.stage.id == 1:
            weld_logs = self.order.weld_logs.all().filter(Q(stage__isnull=True) & Q(user__isnull=True) & Q(status=1))
            locksmith_logs = self.order.locksmith_logs.all().filter(Q(stage__isnull=True) & Q(user__isnull=True) & Q(status=1))
            if not weld_logs.exists() and not locksmith_logs.exists():
                WfWeldLog.objects.create(order=self.order, stage=None)
                WfLocksmithLog.objects.create(order=self.order, stage=None)
        super().save(*args, **kwargs)
        


class WfWeldLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id', related_name='weld_logs')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id', default=WfStageList.DEFAULT_STAGE_ID)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID)
    

    class Meta:
        managed = False
        db_table = 'wf_weld_log'
        
        verbose_name = 'Лог зварювання'
        verbose_name_plural = 'Логи зварювання'


    def __str__(self):
        return self.id
        
        
    def save(self, *args, **kwargs):
        # TODO: check if last log is OK
        
        # locksmith_logs = self.order.locksmith_logs.all().filter(Q(stage__id=1) & Q(user__isnull=False) & Q(status=1))
        # if hasattr(self, 'stage') and self.stage.id == 1 and locksmith_logs:
        #     WfLocksmithLog.objects.create(order=self.order, stage=None)
        super().save(*args, **kwargs)
        


class WfLocksmithLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id', related_name='locksmith_logs')
    stage = models.ForeignKey(WfStageSemiFinishedList, on_delete=models.RESTRICT, db_column='stage_id', default=WfStageSemiFinishedList.DEFAULT_STAGE_ID)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID)
    

    class Meta:
        managed = False
        db_table = 'wf_locksmith_log'
        
        verbose_name = 'Лог слюсарні'
        verbose_name_plural = 'Логи слюсарні'


    def __str__(self):
        return self.id
        
        

class WfGlassLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id', related_name='glass_logs')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id', default=WfStageList.DEFAULT_STAGE_ID)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID)


    class Meta:
        managed = False
        db_table = 'wf_glass_log'
        
        verbose_name = 'Лог скління'
        verbose_name_plural = 'Логи скління'


    def __str__(self):
        return self.id


    def save(self, *args, **kwargs):
        if hasattr(self, 'stage') and self.stage.id == 1:
            WfQualityControlLog.objects.create(order=self.order, stage=None)
        super().save(*args, **kwargs)
        


class WfQualityControlLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id', related_name='quality_logs')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id', default=WfStageList.DEFAULT_STAGE_ID)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID)


    class Meta:
        managed = False
        db_table = 'wf_quality_control_log'
        
        verbose_name = 'Лог контролю якості'
        verbose_name_plural = 'Логи контролю якості'


    def __str__(self):
        return self.id


    def save(self, *args, **kwargs):
        if hasattr(self, 'stage') and self.stage.id == 1:
            WfFinalProductLog.objects.create(order=self.order, stage=None)
        super().save(*args, **kwargs)
        


class WfFinalProductLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id', related_name='final_logs')
    stage = models.ForeignKey(WfStageFinalList, on_delete=models.RESTRICT, db_column='stage_id', default=WfStageFinalList.DEFAULT_STAGE_ID)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID)
    

    class Meta:
        managed = False
        db_table = 'wf_final_product_log'
        
        verbose_name = 'Лог фінального продукту'
        verbose_name_plural = 'Логи фінального продукту'


    def __str__(self):
        return self.id



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
        if self.start_manufacturing and not self.start_date:
            self.start_date = datetime.datetime.now()
        super().save(*args, **kwargs)
        

    def __str__(self):
        return str(self.id)


    def get_absolute_url(self):
        return reverse('workflow:order-detail', kwargs={'pk': self.pk})
