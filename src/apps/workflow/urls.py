from django.urls import path, include
from django.views.generic import TemplateView

from .views import LogListView, OrderUpdateView, OrderDetailView

app_name = 'workflow'

    
urlpatterns = [
    path('', TemplateView.as_view(template_name='main/home.html'), name='home'),
    path('logs/', LogListView.as_view(), name='logs'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('order/<int:pk>/update', OrderUpdateView.as_view(), name='order-update'),
    # path('logs/<int:pk>', WfLogListView.as_view(), name='logs'),
    # path('logs/start_job/<int:id>', views.like_post, name='start_job'),
]