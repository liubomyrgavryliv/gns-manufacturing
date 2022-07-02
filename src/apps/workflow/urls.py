from django.urls import path, include
from django.views.generic import TemplateView

from .views import OrderListView, OrderCreateView, OrderUpdateView, OrderDetailView, NoteListView, start_job, switch_job, add_note

app_name = 'workflow'

    
urlpatterns = [
    path('', TemplateView.as_view(template_name='main/home.html'), name='home'),
    
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update', OrderUpdateView.as_view(), name='order-update'),
    path('orders/add', OrderCreateView.as_view(), name='order-add'),
    
    path('orders/<int:pk>/notes', NoteListView.as_view(), name='order-notes'),
    path('orders/<int:order_id>/notes/add', add_note, name='note-create'),
    
    path('orders/start_job/<int:order_id>', start_job, name='start-job'),
    path('orders/switch_job/<int:order_stage_id>/<int:stage_id>', switch_job, name='switch-job'),
]