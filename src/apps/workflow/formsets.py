from django.forms import BaseModelFormSet, BaseInlineFormSet, formset_factory
from .models.stage import WfWorkStageList
from .models.core import WfOrderWorkStage
from .forms import WfOrderWorkStageForm


class WfWOrderWorkLogFormSet(BaseInlineFormSet):
    
    def __init__(self, *args, **kwargs):        
        kwargs['initial'] = [ 
                             { 'stage': 1, 'order_of_execution': 0 },
                             { 'stage': 2, 'order_of_execution': 1 },
                             { 'stage': 3, 'order_of_execution': 2 },  
                             { 'stage': 4, 'order_of_execution': 3 },
                             { 'stage': 5, 'order_of_execution': 3 },
                             { 'stage': 6, 'order_of_execution': 3 },
                             { 'stage': 7, 'order_of_execution': 4 },
                             { 'stage': 8, 'order_of_execution': 5 },
                             { 'stage': 9, 'order_of_execution': 5 },
                             { 'stage': 10, 'order_of_execution': 6 },
                             { 'stage': 11, 'order_of_execution': 7 },
                            ]
        
        super().__init__(*args, **kwargs)
