from django.contrib import admin

from .models import core as core_models
from .models import stage as stage_models


class WfModelListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]



class WfJobStatusListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]
    
    
    
class WfConfigurationListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]



class WfFireclayTypeListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]
    
    
    
class WfFrameTypeListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]



class WfGlazingTypeListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]
    
    
    
class WfPriorityListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]



class WfQualityControlListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]
    
    
    
class WfPaymentListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]
    
    
    
class WfBendingStationListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]
    
    
    
class WfWeldingStationListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    search_fields = [
        'name',
    ]
    
    
    
class WfDFXVersionControlLogAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'order',
        'stage',
        'status',
    ]
    
    list_select_related = [
        'order',
        'stage',
        'status',
    ]
    
    search_fields = [
        'order',
        'stage',
        'status',
    ]
    
    ordering = ['-order',]
    
    
    
class WfOrderLogAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'model',
        'configuration',
    ]
    
    list_select_related = [
        'model',
        'configuration',
    ]
    
    search_fields = [
        'id',
        'model',
        'configuration',
    ]
    
    ordering = ['-created_at',]
    
    

admin.site.register(core_models.WfModelList, WfModelListAdmin)
admin.site.register(core_models.WfJobStatusList, WfJobStatusListAdmin)
admin.site.register(core_models.WfConfigurationList, WfConfigurationListAdmin)
admin.site.register(core_models.WfFireclayTypeList, WfFireclayTypeListAdmin)
admin.site.register(core_models.WfFrameTypeList, WfFrameTypeListAdmin)
admin.site.register(core_models.WfGlazingTypeList, WfGlazingTypeListAdmin)
admin.site.register(core_models.WfPriorityList, WfPriorityListAdmin)
admin.site.register(core_models.WfQualityControlList, WfQualityControlListAdmin)
admin.site.register(core_models.WfPaymentList, WfPaymentListAdmin)
admin.site.register(core_models.WfBendingStationList, WfBendingStationListAdmin)
admin.site.register(core_models.WfWeldingStationList, WfWeldingStationListAdmin)
admin.site.register(core_models.WfDFXVersionControlLog, WfDFXVersionControlLogAdmin)
admin.site.register(core_models.WfOrderLog, WfOrderLogAdmin)
