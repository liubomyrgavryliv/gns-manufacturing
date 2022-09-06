import datetime

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.models import Q, Min, Max
from django.contrib import admin
from django.utils.html import format_html

from .base import BaseModel, Nameable, Creatable
from .stage import WfStageList, WfStageFinalList, WfWorkStageList


class WfModelList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_model_list'
        ordering = ['name']

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
        ordering = ['name']

        verbose_name = 'Конфігурацію Топки'
        verbose_name_plural = 'Конфігурації Топок'


    def __str__(self):
        return self.name



class WfFireclayTypeList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_fireclay_type_list'
        ordering = ['name']

        verbose_name = 'Тип шамотування'
        verbose_name_plural = 'Типи шамотування'


    def __str__(self):
        return self.name



class WfFrameTypeList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_frame_type_list'
        ordering = ['name']

        verbose_name = 'Тип рами'
        verbose_name_plural = 'Типи рам'


    def __str__(self):
        return self.name



class WfGlazingTypeList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_glazing_type_list'
        ordering = ['name']

        verbose_name = 'Тип скління'
        verbose_name_plural = 'Типи скління'


    def __str__(self):
        return self.name



class WfPriorityList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_priority_list'
        ordering = ['name']

        verbose_name = 'Пріоритет'
        verbose_name_plural = 'Пріоритети'


    def __str__(self):
        return self.name



class WfPaymentList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_payment_list'
        ordering = ['name']

        verbose_name = 'Тип олати'
        verbose_name_plural = 'Типи оплати'


    def __str__(self):
        return self.name



class WfAuthUserGroup(BaseModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True, related_name='work_groups')
    stage = models.ForeignKey(WfWorkStageList, on_delete=models.SET_NULL, db_column='work_stage_id', null=True, related_name='assignees')

    class Meta:
        managed = False
        db_table = 'wf_auth_user_group'

        verbose_name = 'Сферу працівників'
        verbose_name_plural = 'Сфери працівників'


    def __str__(self):
        return str(self.id)

    @admin.display(description='work stage')
    def _stage(self):
        return self.stage.description



class Note(BaseModel, Creatable):

    order = models.ForeignKey('workflow.Order', on_delete=models.RESTRICT, db_column='order_id', related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    note = models.TextField(null=True, blank=False)


    class Meta:
        managed = False
        db_table = 'wf_note_log'

        verbose_name = 'Лог нотатки'
        verbose_name_plural = 'Логи нотаток'

    def __str__(self):
        return self.id



class Order(BaseModel, Creatable):

    model = models.ForeignKey(WfModelList, on_delete=models.CASCADE, db_column='model_id')
    configuration = models.ForeignKey(WfConfigurationList, on_delete=models.CASCADE, db_column='configuration_id')
    fireclay_type = models.ForeignKey(WfFireclayTypeList, on_delete=models.CASCADE, db_column='fireclay_type_id', blank=True, null=True)
    glazing_type = models.ForeignKey(WfGlazingTypeList, on_delete=models.CASCADE, db_column='glazing_type_id', blank=True, null=True)
    frame_type = models.ForeignKey(WfFrameTypeList, on_delete=models.CASCADE, db_column='frame_type_id', blank=True, null=True)
    priority = models.ForeignKey(WfPriorityList, on_delete=models.CASCADE, db_column='priority_id')

    delivery = models.TextField(null=True, blank=True)
    mobile_number = models.TextField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    payment = models.ForeignKey(WfPaymentList, on_delete=models.CASCADE, db_column='payment_id')
    dxf_version = models.CharField(max_length=100, null=True, blank=True)
    serial_number = models.CharField(max_length=100, null=True, blank=True)

    start_manufacturing = models.BooleanField(default=False, help_text='Замовлення починає вироблятись одразу.')
    start_manufacturing_semi_finished = models.BooleanField(default=True, help_text='Замовлення виконується повністю.')
    is_canceled = models.BooleanField(null=False, default=False)
    is_finished = models.BooleanField(null=False, default=False)

    start_date = models.DateTimeField(null=True, blank=True)
    deadline_date = models.DateTimeField(null=True, blank=True)

    work_stages = models.ManyToManyField('workflow.WfWorkStageList', through='WfOrderWorkStage')

    class Meta:
        managed = False
        db_table = 'wf_order_log'
        ordering = ['-created_at']

        verbose_name = 'Лог Замовлень'
        verbose_name_plural = 'Логи Замовлень'

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

        if self.start_manufacturing:
            for work_stage in self.order_stages.all():
                if not work_stage.logs.exists():
                    WfWorkLog.objects.create(work_stage=work_stage, stage=None)

            if self.start_date is None:
                self.start_date = datetime.datetime.now()
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.id)


    def get_absolute_url(self):
        return reverse('workflow:order-detail', kwargs={'pk': self.pk})



class WfOrderWorkStage(BaseModel):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id', related_name='order_stages')
    stage = models.ForeignKey(WfWorkStageList, on_delete=models.RESTRICT, db_column='work_stage_id', null=True)
    order_of_execution = models.IntegerField(null=True)
    is_locked = models.BooleanField(null=False, default=True)

    class Meta:
        managed = False
        db_table = 'wf_order_work_stage'

        verbose_name = 'Стадія замовлення'
        verbose_name_plural = 'Стадії замовлення'

    def __str__(self):
        return str(self.id)


    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if self.order.start_manufacturing and not self.logs.exists():
            WfWorkLog.objects.create(work_stage=self, stage=None)



class WfWorkLog(BaseModel, Creatable):

    work_stage = models.ForeignKey(WfOrderWorkStage, on_delete=models.CASCADE, db_column='order_work_stage_id', related_name='logs')
    stage = models.ForeignKey(WfStageList, on_delete=models.SET_NULL, db_column='stage_id', default=WfStageList.DEFAULT_STAGE_ID, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='user_id', null=True)
    status = models.ForeignKey(WfJobStatusList, on_delete=models.SET_NULL, db_column='status_id', default=WfJobStatusList.DEFAULT_STATUS_ID, null=True)


    class Meta:
        managed = False
        db_table = 'wf_work_log'

        verbose_name = 'Лог виробництва'
        verbose_name_plural = 'Логи виробництва'


    def __str__(self):
        return str(self.id)


@receiver(m2m_changed, sender=WfOrderWorkStage)
def update_order_of_execution(sender, instance, **kwargs):
    action = kwargs.pop('action', None)

    if action in ['post_remove', 'post_add']:

        order_stages = instance.order_stages.all().order_by('stage__id')

        index_ = 0
        max_first_stage_ = order_stages.filter(Q(stage__id__in=[4, 5, 6])).aggregate(max_stage=Max('stage__id'))['max_stage']
        max_second_stage = order_stages.filter(Q(stage__id__in=[8, 9])).aggregate(max_stage=Max('stage__id'))['max_stage']

        for order_stage in order_stages:
            stage = order_stage.stage.id

            if stage in [4, 5, 6, 8, 9]:
                order_stage.order_of_execution = index_

                if stage in [max_first_stage_, max_second_stage]:
                    index_ += 1
            else:
                order_stage.order_of_execution = index_
                index_ += 1

            order_stage.save()
