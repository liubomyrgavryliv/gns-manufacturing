from django.db.models import Q
from django.forms import ModelForm, Textarea, EmailInput, ModelMultipleChoiceField, CheckboxSelectMultiple, IntegerField
from django.utils.translation import gettext_lazy as _

from .models.core import Note, Order, OrderWorkStage, WfModelList
from .models.stage import WfWorkStageList
from .widgets import MinimalSplitDateTimeMultiWidget

class ModelForm(ModelForm):

    class Meta:
        model = WfModelList
        fields = ['name',]
        labels = {
            'name': _('Назва моделі'),
        }


class NoteLogForm(ModelForm):

    class Meta:
        model = Note
        fields = ['note',]



class OrderWorkStageForm(ModelForm):

    class Meta:
        model = OrderWorkStage
        fields = [
            'stage',
            'order_of_execution',
        ]
        labels = {
            'stage': _('Стадія виконання'),
            'order_of_execution': _('Порядок виконання'),
        }

    def has_changed(self):
        return not self.instance.pk or super().has_changed()



class CustomMMCF(ModelMultipleChoiceField):

    def label_from_instance(self, instance):
        return "%s" % instance.description



class OrderForm(ModelForm):

    work_stages = CustomMMCF(
        label='Стадії виконання',
        queryset=WfWorkStageList.objects.filter(~Q(id=12)),
        widget=CheckboxSelectMultiple,
        required=False
    )

    number_of_orders = IntegerField(max_value=20,
                                    min_value=1,
                                    initial=1,
                                    label='Кількість замовлень',
                                    help_text='Введіть кількість ідентичних замовлень, які буде створено (максимум 20).')

    class Meta:
        model = Order
        fields = ['model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'priority', 'delivery',
                  'mobile_number', 'email', 'payment', 'dxf_version', 'serial_number', 'start_date', 'deadline_date', 'start_manufacturing',
                  'start_manufacturing_semi_finished', 'work_stages',]
        labels = {
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
            'dxf_version': _('DXF версія'),
            'serial_number': _('Серійний Номер'),
            'start_date': _('Початок виконання'),
            'deadline_date': _('Дедлайн виконання'),
            'start_manufacturing': _('Віддати в роботу?'),
            'start_manufacturing_semi_finished': _('Автоматично продовжити виконання після виготовлення напівфабрикату?'),
            'work_stages': _('Стадії виконання'),
            'number_of_orders': _('Кількість ідентичних замовлень'),
        }
        widgets = {
            'email': EmailInput(),
            'delivery': Textarea(attrs={'cols': 20, 'rows': 2}),
            'mobile_number': Textarea(attrs={'cols': 20, 'rows': 1}),
            'start_date': MinimalSplitDateTimeMultiWidget(),
            'deadline_date': MinimalSplitDateTimeMultiWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        text_field_css_ = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-md focus:ring-blue-500 focus:border-blue-500 block w-full p-2'
        date_field_css_ = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-md focus:ring-blue-500 focus:border-blue-500 flex flex-row p-2'

        self.fields['model'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['configuration'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['fireclay_type'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['glazing_type'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['frame_type'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['priority'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['delivery'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['mobile_number'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['email'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['payment'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['dxf_version'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['serial_number'].widget.attrs.update({ 'class': text_field_css_ })
        self.fields['number_of_orders'].widget.attrs.update({ 'class': text_field_css_ })

        self.fields['start_date'].widget.attrs.update({ 'class': date_field_css_ })
        self.fields['deadline_date'].widget.attrs.update({ 'class': date_field_css_ })

    def clean(self):
        cleaned_data = super().clean()

        start_manufacturing = cleaned_data.get("start_manufacturing")
        work_stages = cleaned_data.get("work_stages")

        if start_manufacturing and not work_stages:
            self.add_error('work_stages', "Задайте стадії виробництва, перед подачею в роботу!")

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=commit)
        work_stages = self.cleaned_data.get('work_stages')

        if 'number_of_orders' in self.cleaned_data:
            for i in range(self.cleaned_data['number_of_orders'] - 1):
                order.pk = None
                order._state.adding = True
                order.save()
                order.work_stages.set(work_stages)

        return order
