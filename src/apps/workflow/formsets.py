from django.forms import BaseInlineFormSet
from .models.stage import WfWorkStageList


class WfWOrderWorkLogFormSet(BaseInlineFormSet):
    
    model = WfWorkStageList
    
    def __init__(self, *args, **kwargs):        
        kwargs['initial'] = [ { 'id': 1 } ]
        super().__init__(*args, **kwargs)

