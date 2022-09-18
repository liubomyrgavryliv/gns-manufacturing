from django.db import models

from .base import BaseModel, Nameable

class WfStageList(BaseModel, Nameable):

    DEFAULT_STAGE_ID = 2

    class Meta:
        managed = False
        db_table = 'wf_stage_list'


    def __str__(self):
        return self.name



class WfWorkStageList(BaseModel, Nameable):

    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)

    DEFAULT_STAGE_ID = 1

    class Meta:
        managed = False
        db_table = 'wf_work_stage_list'

        verbose_name = 'Стадію виконання роботи'
        verbose_name_plural = 'Стадії виконання роботи'


    def __str__(self):
        return self.name



class OrderStatusList(BaseModel, Nameable):

    DEFAULT_STATUS_ID = 1

    class Meta:
        managed = False
        db_table = 'wf_order_status_list'

        verbose_name = 'Статус замовлення'
        verbose_name_plural = 'Статуси замовлень'


    def __str__(self):
        return self.name
