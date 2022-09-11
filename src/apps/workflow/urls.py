from django.urls import path
from django.views.generic import TemplateView

from .views import (OrderListView, OrderCreateView, OrderUpdateView, OrderDetailView,
                    NoteListView, ModelListView, ModelUpdateView, add_model, start_job,
                    start_second_stage, cancel_job, switch_job, add_note, add_delivery_job)


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
    path('orders/cancel_job/<int:order_id>', cancel_job, name='cancel-job'),
    path('orders/start_second_stage/<int:order_id>', start_second_stage, name='start-second-stage'),
    path('orders/switch_job/<int:order_id>/<int:stage_id>', switch_job, name='switch-job'),
    path('orders/add_delivery_job/<int:order_id>', add_delivery_job, name='add-delivery-job'),


    path('models/', ModelListView.as_view(), name='models'),
    path('models/add', add_model, name='model-add'),
    path('models/<int:pk>/update', ModelUpdateView.as_view(), name='model-update'),
]
