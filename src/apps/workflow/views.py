from django.db.models import Q, Count
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models.core import WfDFXVersionControlLog, WfOrderLog


class WfLogListView(LoginRequiredMixin, ListView):

    http_method_names = ['get', 'head', 'options', 'trace']

    queryset = WfOrderLog.objects.filter(Q(start_manufacturing=True) & Q(dfx_logs__isnull=True))
    ordering = ['priority__id', '-start_date', 'deadline_date',]

    context_object_name = 'logs'
    
    template_name = 'workflow/dfx_log_list.html'
