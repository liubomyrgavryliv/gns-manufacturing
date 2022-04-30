from django.urls import path, include
from django.views.generic import TemplateView

from .views import WfLogListView

app_name = 'workflow'

    
urlpatterns = [
    path('', TemplateView.as_view(template_name='main/home.html'), name='home'),
    path('logs/', WfLogListView.as_view(), name='logs'),
]