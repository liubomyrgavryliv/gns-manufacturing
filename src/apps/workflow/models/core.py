from django.db import models

from .base import BaseModel, Nameable, Creatable, Updatable
from .stage import WfStageList, WfStageSemiFinishedList, WfStageFinalList


class WfModelList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_model_list'
        verbose_name_plural = 'Моделі Топок'


    def __str__(self):
        return self.name



class WfJobStatusList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_job_status_list'
        verbose_name_plural = 'Статуси виконання робіт'


    def __str__(self):
        return self.name
    
    

class WfConfigurationList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_configuration_list'
        verbose_name_plural = 'Конфігурації Топок'


    def __str__(self):
        return self.name



class WfFireclayTypeList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_fireclay_type_list'
        verbose_name_plural = 'Типи шамотування'


    def __str__(self):
        return self.name



class WfFrameTypeList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_frame_type_list'
        verbose_name_plural = 'Типи рам'


    def __str__(self):
        return self.name



class WfGlazingTypeList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_glazing_type_list'
        verbose_name_plural = 'Типи скління'


    def __str__(self):
        return self.name



class WfPriorityList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_priority_list'
        verbose_name_plural = 'Пріоритети'


    def __str__(self):
        return self.name



class WfQualityControlList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_quality_control_list'
        verbose_name_plural = 'Контролі якості'


    def __str__(self):
        return self.name



class WfPaymentList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_payment_list'
        verbose_name_plural = 'Типи оплати'


    def __str__(self):
        return self.name



class WfBendingStationList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_bending_station_list'
        verbose_name_plural = 'Станції гнуття'


    def __str__(self):
        return self.name



class WfWeldingStationList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'wf_welding_station_list'
        verbose_name_plural = 'Станції зварювання'


    def __str__(self):
        return self.name



class WfDFXVersionControlLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id')
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id')
    

    class Meta:
        managed = False
        db_table = 'wf_dfx_version_control_log'
        verbose_name_plural = 'Логи DFX Версій'


    def __str__(self):
        return self.id



class WfCutLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id')
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id')
    verbose_name_plural = 'Логи різки'
    

    class Meta:
        managed = False
        db_table = 'wf_cut_log'


    def __str__(self):
        return self.id



class WfBendLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id')
    machine = models.ForeignKey(WfBendingStationList, on_delete=models.RESTRICT, db_column='machine_id')
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id')
    

    class Meta:
        managed = False
        db_table = 'wf_bend_log'
        verbose_name_plural = 'Логи гнуття'


    def __str__(self):
        return self.id



class WfWeldLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id')
    machine = models.ForeignKey(WfWeldingStationList, on_delete=models.RESTRICT, db_column='machine_id')
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id')
    

    class Meta:
        managed = False
        db_table = 'wf_weld_log'
        verbose_name_plural = 'Логи зварювання'


    def __str__(self):
        return self.id



class WfLocksmithLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id')
    stage = models.ForeignKey(WfStageSemiFinishedList, on_delete=models.RESTRICT, db_column='stage_id')
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id')
    

    class Meta:
        managed = False
        db_table = 'wf_locksmith_log'
        verbose_name_plural = 'Логи слюсарні'


    def __str__(self):
        return self.id



class WfGlassLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id')
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id')
    

    class Meta:
        managed = False
        db_table = 'wf_glass_log'
        verbose_name_plural = 'Логи скління'


    def __str__(self):
        return self.id



class WfQualityControlLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id')
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id')
    

    class Meta:
        managed = False
        db_table = 'wf_quality_control_log'
        verbose_name_plural = 'Логи контролю якості'


    def __str__(self):
        return self.id



class WfFinalProductLog(BaseModel, Creatable):

    order = models.ForeignKey('workflow.WfOrderLog', on_delete=models.RESTRICT, db_column='order_id')
    stage = models.ForeignKey(WfStageFinalList, on_delete=models.RESTRICT, db_column='stage_id')
    status = models.ForeignKey(WfJobStatusList, on_delete=models.RESTRICT, db_column='status_id')
    

    class Meta:
        managed = False
        db_table = 'wf_final_product_log'
        verbose_name_plural = 'Логи фінального продукту'


    def __str__(self):
        return self.id



class WfOrderLog(BaseModel, Creatable):

    model = models.ForeignKey(WfModelList, on_delete=models.CASCADE, db_column='model_id')
    configuration = models.ForeignKey(WfConfigurationList(), on_delete=models.CASCADE, db_column='configuration_id')
    fireclay_type = models.ForeignKey(WfFireclayTypeList, on_delete=models.CASCADE, db_column='fireclay_type_id')
    glazing_type = models.ForeignKey(WfGlazingTypeList, on_delete=models.CASCADE, db_column='glazing_type_id')
    frame_type = models.ForeignKey(WfFrameTypeList, on_delete=models.CASCADE, db_column='frame_type_id')
    priority = models.ForeignKey(WfPriorityList, on_delete=models.CASCADE, db_column='priority_id')

    note = models.TextField(null=True, blank=True)

    delivery = models.TextField(null=True, blank=True)
    mobile_number = models.TextField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    payment = models.ForeignKey(WfPaymentList, on_delete=models.CASCADE, db_column='payment_id')

    start_manufacturing = models.BooleanField(default=False)

    start_date = models.DateTimeField(null=True) # start_date triggers when start_manufacturing is True
    deadline_date = models.DateTimeField(null=True)

    dfx_logs = models.ManyToManyField(WfStageList, through=WfDFXVersionControlLog, related_name='dfx_orders')
    cut_logs = models.ManyToManyField(WfStageList, through=WfCutLog, related_name='cut_orders')
    bend_logs = models.ManyToManyField(WfStageList, through=WfBendLog, related_name='bend_orders')
    weld_logs = models.ManyToManyField(WfStageList, through=WfWeldLog, related_name='weld_orders')
    locksmith_logs = models.ManyToManyField(WfStageSemiFinishedList, through=WfLocksmithLog, related_name='locksmith_orders')
    glazing_logs = models.ManyToManyField(WfStageList, through=WfGlassLog, related_name='glazing_orders')
    quality_logs = models.ManyToManyField(WfStageList, through=WfQualityControlLog, related_name='quality_orders')
    final_logs = models.ManyToManyField(WfStageFinalList, through=WfFinalProductLog, related_name='final_orders')


    class Meta:
        managed = False
        db_table = 'wf_order_log'
        verbose_name_plural = 'Логи Замовлень'


    def __str__(self):
        return self.id
