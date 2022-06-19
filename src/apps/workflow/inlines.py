from django.contrib import admin

from .models import core as core_models
from .formsets import WfWOrderWorkLogFormSet


class WfOrderWorkStageInline(admin.TabularInline):
    model = core_models.WfOrderWorkStage
    
    extra = 1
