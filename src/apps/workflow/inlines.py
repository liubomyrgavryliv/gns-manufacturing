from django.contrib import admin

from .models import core as core_models
from .forms import OrderWorkStageForm


class OrderWorkStageInline(admin.TabularInline):
    model = core_models.OrderWorkStage
    form = OrderWorkStageForm

    extra = 1
