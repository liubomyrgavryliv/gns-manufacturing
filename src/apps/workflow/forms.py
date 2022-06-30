from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
 
from .models.core import WfNoteLog, WfOrderLog, WfOrderWorkStage
 
 
 
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
