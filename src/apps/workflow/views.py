from django.db.models import Q, Count
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models.core import WfDFXVersionControlLog, WfOrderLog


class WfLogListView(LoginRequiredMixin, ListView):

    http_method_names = ['get', 'head', 'options', 'trace']

    queryset = WfOrderLog.objects.filter(Q(start_manufacturing=True) & Q(dfx_logs__isnull=False))
    ordering = ['priority__id', '-start_date', 'deadline_date',]

    context_object_name = 'logs'
    
    template_name = 'workflow/dfx_log_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        queryset = queryset.select_related('model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'priority')
        
        return queryset



def start_job(request, id):
    post = get_object_or_404(WfOrderLog, id=id)
    is_liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    return HttpResponseRedirect(post.get_absolute_url())