from django.contrib import admin
from django.forms import inlineformset_factory, modelformset_factory

from .models.stage import WfWorkStageList
from .models import core as core_models
from .formsets import WfWOrderWorkLogFormSet
from .forms import WfOrderWorkStageForm


class WfOrderWorkStageInline(admin.TabularInline):
    model = core_models.WfOrderWorkStage
    form = WfOrderWorkStageForm
    formset = WfWOrderWorkLogFormSet
    
    extra = 10
