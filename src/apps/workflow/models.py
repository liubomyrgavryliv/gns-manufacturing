from django.db import models


class WfModelList(models.Model):

    id = models.AutoField(primary_key=True, db_column='model_id')
    name = models.CharField(max_length=100, db_column='model_name')

    class Meta:
        db_table = 'wf_model_list'


    def __str__(self):
        return self.name



class WfConfigurationList(models.Model):

    id = models.AutoField(primary_key=True, db_column='configuration_id')
    name = models.CharField(max_length=100, db_column='configuration_name')

    class Meta:
        db_table = 'wf_configuration_list'


    def __str__(self):
        return self.name



class WfFireclayTypeList(models.Model):

    id = models.AutoField(primary_key=True, db_column='fireclay_type_id')
    name = models.CharField(max_length=100, db_column='fireclay_type_name')

    class Meta:
        db_table = 'wf_fireclay_type_list'


    def __str__(self):
        return self.name



class WfFrameTypeList(models.Model):

    id = models.AutoField(primary_key=True, db_column='frame_type_id')
    name = models.CharField(max_length=100, db_column='frame_type_name')

    class Meta:
        db_table = 'wf_frame_type_list'


    def __str__(self):
        return self.name



class WfGlazingTypeList(models.Model):

    id = models.AutoField(primary_key=True, db_column='glazing_type_id')
    name = models.CharField(max_length=100, db_column='glazing_type_name')

    class Meta:
        db_table = 'wf_glazing_type_list'


    def __str__(self):
        return self.name



class WfPriorityList(models.Model):

    id = models.AutoField(primary_key=True, db_column='priority_id')
    name = models.CharField(max_length=100, db_column='priority_name')

    class Meta:
        db_table = 'wf_priority_list'


    def __str__(self):
        return self.name



class WfStageList(models.Model):

    id = models.AutoField(primary_key=True, db_column='stage_id')
    name = models.CharField(max_length=100, db_column='stage_name')

    class Meta:
        db_table = 'wf_stage_list'


    def __str__(self):
        return self.name



class WfSemiFinishedStageList(models.Model):

    id = models.AutoField(primary_key=True, db_column='semi_finished_stage_id')
    name = models.CharField(max_length=100, db_column='semi_finished_stage_name')

    class Meta:
        db_table = 'wf_semi_finished_stage_list'


    def __str__(self):
        return self.name



class WfQualityControlList(models.Model):

    id = models.AutoField(primary_key=True, db_column='quality_control_id')
    name = models.CharField(max_length=100, db_column='quality_control_name')

    class Meta:
        db_table = 'wf_quality_control_list'


    def __str__(self):
        return self.name



class WfQualityControlList(models.Model):

    id = models.AutoField(primary_key=True, db_column='quality_control_id')
    name = models.CharField(max_length=100, db_column='quality_control_name')

    class Meta:
        db_table = 'wf_quality_control_list'


    def __str__(self):
        return self.name



class WfTaskList(models.Model):

    id = models.AutoField(primary_key=True, db_column='task_id')
    name = models.CharField(max_length=100, db_column='task_name')

    class Meta:
        db_table = 'wf_task_list'


    def __str__(self):
        return self.name



class WfDFXVersionControlLog(models.Model):

    id = models.AutoField(primary_key=True, db_column='dfx_version_control_id')
    order = models.ForeignKey(WfOrderLog, on_delete=models.RESTRICT, db_column='order_id')
    stage = models.ForeignKey(WfStageList, on_delete=models.RESTRICT, db_column='stage_id')
    date = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        db_table = 'wf_dfx_version_control_log'


    def __str__(self):
        return self.id



class WfOrderLog(models.Model):

    id = models.AutoField(primary_key=True, db_column='order_id')

    model = models.ForeignKey(WfModelList, on_delete=models.CASCADE, db_column='model_id')
    configuration = models.ForeignKey(WfConfigurationList(), on_delete=models.CASCADE, db_column='configuration_id')
    fireclay_type = models.ForeignKey(WfFireclayTypeList, on_delete=models.CASCADE, db_column='fireclay_type_id')
    glazing_type = models.ForeignKey(WfGlazingTypeList, on_delete=models.CASCADE, db_column='glazing_type_id')
    frame_type = models.ForeignKey(WfFrameTypeList, on_delete=models.CASCADE, db_column='frame_type_id')
    priority = models.ForeignKey(WfPriorityList, on_delete=models.CASCADE, db_column='priority_id')

    note = models.TextField(null=True, blank=True)

    # TODO: how to store payment types?

    # payment = 
    delivery = models.TextField(null=True, blank=True)
    mobile_number = models.TextField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()

    dfx_versions = models.ManyToManyField(WfStageList, through=WfDFXVersionControlLog, related_name='orders')

    class Meta:
        db_table = 'wf_order_log'


    def __str__(self):
        return self.id