from django.contrib import admin

from .models import core as core_models
from .forms import WfOrderWorkStageForm


class WfOrderWorkStageInline(admin.TabularInline):
    model = core_models.WfOrderWorkStage
    form = WfOrderWorkStageForm

    extra = 1
