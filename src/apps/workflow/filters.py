from django import forms
from django.db.models import Q, OuterRef, Max, Exists, Subquery, IntegerField, Case, When, Value
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _
import django_filters as filters

from .models.core import Order, OrderStatus, Note
from .models.stage import OrderStatusList

STATUS_CHOICES = (
    (0, 'Всі, крім скасовано'),
    (1, 'В роботі'),
    (2, 'Виготовлено'),
    (3, 'Відправлено'),
    (4, 'Скасовано'),
)


class OrderFilter(filters.FilterSet):

    start_date = filters.DateTimeFilter(widget=AdminDateWidget(attrs={ 'type': 'datetime-local' }), lookup_expr='lte')
    deadline_date = filters.DateTimeFilter(widget=AdminDateWidget(attrs={ 'type': 'datetime-local' }), lookup_expr='gte')
    statuses = filters.ChoiceFilter(choices=STATUS_CHOICES, method='filter_statuses')
    # statuses = filters.ModelChoiceFilter(queryset=OrderStatusList.objects.all(),
    #                                      to_field_name='id',
    #                                      label=_('Статус'),
    #                                      method='filter_statuses',
    #                                      empty_label=_('Всі, крім скасовано'))
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
                  'statuses', 'start_date', 'deadline_date',]

    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        data.setdefault('statuses', 0)
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
        self.filters['statuses'].field.widget.attrs.update({ 'class': text_field_css_ })
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
            'statuses': _('Статус'),
            'ordering': _('Сортування')
        }
        for filter in self.filters:
            self.filters[filter].field.label = labels_[filter]


    def filter_statuses(self, queryset, name, value):
        value = int(value)
        max_status_ = OrderStatus.objects.values('order').annotate(max_id=Max('id'))
        max_status = OrderStatus.objects.filter(Q(id__in=max_status_.values('max_id')) & (Q(order__id=OuterRef('id'))))

        if value == 0:
            print('asFsafsafasf')
            return queryset.annotate(max_status=Case(
                                                    When(
                                                        Exists(OrderStatus.objects.filter(Q(order=OuterRef('id')) & Q(status__isnull=False))),
                                                        then=Subquery(max_status.values('status'))
                                                        ),
                                                    default=None,
                                                )
                                    ).filter(~Q(max_status=4) | Q(max_status__isnull=True))
        return queryset.annotate(max_status=Subquery(max_status.values('status'))).filter(max_status=value)



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
