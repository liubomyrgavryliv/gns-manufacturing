from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _
import django_filters as filters

from .models.core import Order, Note

class OrderFilter(filters.FilterSet):

    start_date = filters.DateTimeFilter(widget=AdminDateWidget(attrs={ 'type': 'datetime-local' }), lookup_expr='lte')
    deadline_date = filters.DateTimeFilter(widget=AdminDateWidget(attrs={ 'type': 'datetime-local' }), lookup_expr='gte')
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('model', 'model'),
            ('configuration', 'configuration'),
            ('fireclay_type', 'fireclay_type'),
            ('glazing_type', 'glazing_type'),
            ('priority', 'priority'),
            ('payment', 'payment'),
            ('start_date', 'start_date'),
            ('deadline_date', 'deadline_date'),
        ),
        field_labels={
            'id': 'id замовлення',
             'model': 'Модель',
            'configuration': 'Конфігурація',
            'fireclay_type': 'Шамотування',
            'glazing_type': 'Тип скління',
            'priority': 'Пріоритет',
            'payment': 'Оплата',
            'start_date': 'Дата початку виробництва',
            'deadline_date': 'Дата дедлайну',
        }
    )

    class Meta:
        model = Order
        fields = ['ordering', 'model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'priority', 'payment', 'start_manufacturing',
                  'is_canceled', 'start_date', 'deadline_date',]

    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        data.setdefault('is_canceled', False)
        super().__init__(data, *args, **kwargs)

        text_field_css_ = 'bg-gray-50 border border-gray-300 shadow-sm text-black rounded focus:ring-blue-500 focus:border-blue-500 block p-1 text-xs md:text-sm w-2/3 justify-center'
        date_field_css_ = 'bg-gray-50 border border-gray-300 shadow-sm text-black rounded focus:ring-blue-500 focus:border-blue-500 text-xs md:text-sm col-span-2'

        self.filters['model'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['configuration'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['fireclay_type'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['glazing_type'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['frame_type'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['priority'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['payment'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['start_manufacturing'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['is_canceled'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['ordering'].field.widget.attrs.update({ 'class': text_field_css_ })

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
            'start_date': _('Початок виконання >='),
            'deadline_date': _('Дедлайн виконання <='),
            'start_manufacturing': _('В роботі'),
            'is_canceled': _('Скасовано'),
            'ordering': _('Сортування')
        }
        for filter in self.filters:
            self.filters[filter].field.label = labels_[filter]



class NoteFilter(filters.FilterSet):

    class Meta:
        model = Note
        fields = ['order', 'user',]

    def __init__(self, data, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        text_field_css_ = 'bg-gray-50 border border-gray-300 shadow-sm text-black rounded focus:ring-blue-500 focus:border-blue-500 block p-1 text-xs md:text-sm'

        self.filters['user'].field.widget.attrs.update({ 'class': text_field_css_ })
        self.filters['order'].field.widget.attrs.update({ 'class': text_field_css_ })

        labels_ = {
            'user': _('Працівник'),
        }
        for filter in self.filters:
            self.filters[filter].field.label = labels_[filter]
