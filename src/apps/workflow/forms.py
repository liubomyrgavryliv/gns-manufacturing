from django.forms import ModelForm
 
from .models.core import WfNoteLog
 
 
 
class WfNoteLogForm(ModelForm):
    
    class Meta:
        model = WfNoteLog
        fields = ['note',]
