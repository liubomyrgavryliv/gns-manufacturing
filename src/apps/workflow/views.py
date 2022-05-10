from django.db.models import Q, Count
from django.views.generic import ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models.core import WfOrderLog


class LogListView(LoginRequiredMixin, ListView):

    http_method_names = ['get', 'head', 'options', 'trace']

    queryset = WfOrderLog.objects.filter(Q(start_manufacturing=True) & Q(dfx_logs__isnull=False))
    ordering = ['priority__id', '-start_date', 'deadline_date',]

    context_object_name = 'logs'
    
    template_name = 'workflow/dfx_log_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        queryset = queryset.select_related('model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'priority')
        
        return queryset



class OrderDetailView(LoginRequiredMixin, DetailView):
    
    http_method_names = ['get', 'head', 'options', 'trace']
    
    context_object_name = 'publisher'
    # queryset = Publisher.objects.all()
    
    template_name = 'workflow/order_detail.html'
    


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'trace']
    
    model = WfOrderLog
    fields = ['model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'note',]
    
    template_name = 'workflow/order_update.html'

# def start_job(request, id):
#     post = get_object_or_404(WfOrderLog, id=id)
#     is_liked = False
#     if post.likes.filter(id=request.user.id).exists():
#         post.likes.remove(request.user)
#         is_liked = False
#     else:
#         post.likes.add(request.user)
#         is_liked = True
#     return HttpResponseRedirect(post.get_absolute_url())