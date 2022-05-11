from django.urls import path, include
from django.views.generic import TemplateView

from .views import OrderListView, OrderUpdateView, OrderDetailView, start_job, finish_job

app_name = 'workflow'

    
urlpatterns = [
    path('', TemplateView.as_view(template_name='main/home.html'), name='home'),
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update', OrderUpdateView.as_view(), name='order-update'),
    path('orders/start_job/<int:id>', start_job, name='start-job'),
    path('orders/finish_job/<int:id>', finish_job, name='finish-job'),
]