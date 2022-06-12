from django.contrib import admin

from .models import core as core_models
from .formsets import WfWOrderWorkLogFormSet

    
class WfDXFVersionControlLogInline(admin.TabularInline):
    model = core_models.WfDXFVersionControlLog
    
    extra = 1
    
    
    
class WfCutLogInline(admin.TabularInline):
    model = core_models.WfCutLog
    
    extra = 1
    
    
    
class WfBendLogInline(admin.TabularInline):
    model = core_models.WfBendLog
    
    extra = 1
    
    
    
class WfWeldLogInline(admin.TabularInline):
    model = core_models.WfWeldLog
    
    extra = 1
    
    
    
class WfLocksmithLogInline(admin.TabularInline):
    model = core_models.WfLocksmithLog
    
    extra = 1
    
    
    
class WfGlassLogInline(admin.TabularInline):
    model = core_models.WfGlassLog
    
    extra = 1
    
    
    
class WfQualityControlLogInline(admin.TabularInline):
    model = core_models.WfQualityControlLog
    
    extra = 1
    
    
    
class WfFinalProductLogInline(admin.TabularInline):
    model = core_models.WfFinalProductLog
    
    extra = 1



class WfOrderWorkStageInline(admin.TabularInline):
    model = core_models.WfOrderWorkStage
    
    extra = 8
