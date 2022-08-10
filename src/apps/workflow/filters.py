from django.forms import SelectDateWidget
from django.utils.translation import gettext_lazy as _
import django_filters as filters

from .models.core import Order

class OrderFilter(filters.FilterSet):

    start_date = filters.DateFilter(widget=SelectDateWidget())
    deadline_date = filters.DateFilter(widget=SelectDateWidget())

    class Meta:
        model = Order
        fields = ['model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'priority', 'payment', 'start_manufacturing',
                  'start_date', 'deadline_date', 'is_canceled',]

    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        data.setdefault('is_canceled', False)
        super().__init__(data, *args, **kwargs)

        text_field_css_ = 'bg-gray-50 border border-gray-300 border-gray-200 shadow-sm text-gray-900 rounded-md focus:ring-blue-500 focus:border-blue-500 block w-full p-2 text-xs md:text-sm'
        date_field_css_ = 'bg-gray-50 border border-gray-300 text-gray-900 shadow-sm rounded-md focus:ring-blue-500 focus:border-blue-500 flex flex-row p-2 text-xs md:text-sm'

        self.filters['model'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['configuration'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['fireclay_type'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['glazing_type'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['frame_type'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['priority'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['payment'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['start_manufacturing'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['is_canceled'].field.widget.attrs.update({ 'class': text_field_css_ })

        self.filters['start_date'].field.widget.attrs.update({ 'class': date_field_css_ })
        self.filters['deadline_date'].field.widget.attrs.update({ 'class': date_field_css_ })

        labels_ = {
            'model': _('Модель топки'),
            'configuration': _('Конфігурація'),
            'fireclay_type': _('Тип шамотування'),
            'glazing_type': _('Тип скління'),
            'frame_type': _('Тип рами'),
            'priority': _('Пріоритет'),
            'delivery': _('Доставка'),
            'mobile_number': _('Номер телефону'),
            'email': _('e-mail'),
            'payment': _('Оплата'),
            'start_date': _('Початок виконання'),
            'deadline_date': _('Дедлайн виконання'),
            'start_manufacturing': _('В роботі'),
            'is_canceled': _('Скасовано')
        }
        for filter in self.filters:
            self.filters[filter].field.label = labels_[filter]
