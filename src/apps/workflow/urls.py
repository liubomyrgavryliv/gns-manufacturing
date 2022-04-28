from django.urls import path, include
from django.views.generic import TemplateView

from . import views as views

app_name = 'workflow'

    
urlpatterns = [
    path('', TemplateView.as_view(template_name='main/home.html'), name='home'),
]