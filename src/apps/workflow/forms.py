from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
 
from .models.core import WfNoteLog, WfOrderLog
 
 
 
class WfNoteLogForm(ModelForm):
    
    class Meta:
        model = WfNoteLog
        fields = ['note',]



class WfOrderLogForm(ModelForm):
    
    class Meta:
        model = WfOrderLog
        fields = ['model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'priority', 'deadline_date',]
        labels = {
            'model': _('Модель топки'),
            'configuration': _('Конфігурація'),
            'fireclay_type': _('Тип шамотування'),
            'glazing_type': _('Тип скління'),
            'frame_type': _('Тип рами'),
            'priority': _('Пріоритет'),
            'deadline_date': _('Дедлайн виконання'),
        }
