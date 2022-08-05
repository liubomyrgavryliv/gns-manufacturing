from django.forms import ModelForm, Textarea, SelectDateWidget, EmailInput, ModelMultipleChoiceField, CheckboxSelectMultiple, modelformset_factory, inlineformset_factory
from django.utils.translation import gettext_lazy as _
 
from .formsets import WfWOrderWorkLogFormSet
from .models.core import WfNoteLog, WfOrderLog, WfOrderWorkStage, WfModelList
from .models.stage import WfStageList, WfWorkStageList
 
 
class ModelForm(ModelForm):
    
    class Meta:
        model = WfModelList
        fields = ['name',]
        labels = {
            'name': _('Назва моделі'),
        }
 
 
class WfNoteLogForm(ModelForm):
    
    class Meta:
        model = WfNoteLog
        fields = ['note',]



class WfOrderWorkStageForm(ModelForm):
    
    class Meta:
        model = WfOrderWorkStage
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



class WfOrderLogForm(ModelForm):
    
    work_stages = CustomMMCF(
        label='Стадії виконання',
        queryset=WfWorkStageList.objects.all(),
        widget=CheckboxSelectMultiple
    )
    
        
    class Meta:
        model = WfOrderLog
        fields = ['model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'priority', 'delivery',
                  'mobile_number', 'email', 'payment', 'start_date', 'deadline_date', 'start_manufacturing', 'start_manufacturing_semi_finished',
                  'work_stages',]
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
            'start_date': _('Початок виконання'),
            'deadline_date': _('Дедлайн виконання'),
            'start_manufacturing': _('Віддати в роботу?'),
            'start_manufacturing_semi_finished': _('Автоматично продовжити виконання після виготовлення напівфабрикату?'),
            'work_stages': _('Стадії виконання'),
        }
        widgets = {
            'email': EmailInput(),
            'delivery': Textarea(attrs={'cols': 20, 'rows': 2}),
            'mobile_number': Textarea(attrs={'cols': 20, 'rows': 1}),
            'start_date': SelectDateWidget(),
            'deadline_date': SelectDateWidget(),
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
        
        self.fields['start_date'].widget.attrs.update({ 'class': date_field_css_ })
        self.fields['deadline_date'].widget.attrs.update({ 'class': date_field_css_ })
