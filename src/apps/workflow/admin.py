from django.contrib import admin
from django.contrib import messages
from django.db import models
from django.forms import TextInput, Textarea
from django.utils.translation import ngettext

from .models import core as core_models
from .models import stage as stage_models
from . import inlines as inlines


class WfModelListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    list_editable = ['name',]
    
    search_fields = [
        'name',
    ]



class WfJobStatusListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    list_display_links = ['name',]
    
    search_fields = [
        'name',
    ]    
    
    
    
class WfConfigurationListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    list_display_links = ['name',]
    
    search_fields = [
        'name',
    ]    



class WfFireclayTypeListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    list_display_links = ['name',]
    
    search_fields = [
        'name',
    ]    
    
    
    
class WfFrameTypeListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    list_display_links = ['name',]
    
    search_fields = [
        'name',
    ]    



class WfGlazingTypeListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    list_display_links = ['name',]
    
    search_fields = [
        'name',
    ]    
    
    
    
class WfPriorityListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    list_display_links = ['name',]
    
    search_fields = [
        'name',
    ]    

    
    
class WfPaymentListAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        'name',
    ]
    
    list_display_links = ['name',]
    
    search_fields = [
        'name',
    ]       
    
    
    
class WfDFXVersionControlLogAdmin(admin.ModelAdmin):
    
    list_display = [
        'id',
        
        'order',
        'stage',
        'status',
    ]    
    
    list_display_links = ['order', 'stage', 'status',]
    
    list_select_related = [
        'order',
        'stage',
        'status',
    ]
    
    search_fields = [
        'order',
        'stage',
        'status',
    ]
    
    ordering = ['-order',]
    
    
    
class WfOrderLogAdmin(admin.ModelAdmin):

    actions = ['send_to_work']

    def send_to_work(self, request, queryset):
        try:
            for log in queryset:
                log.start_manufacturing = True
                log.save()

            self.message_user(request, ngettext(
                '%d замовлення було відправлено в роботу!',
                '%d замовлень було відправлено в роботу!',
                len(queryset),
            ) % len(queryset), messages.SUCCESS)

        except Exception as e:
            self.message_user(request, e, messages.ERROR)

    send_to_work.short_description = 'Відправити в роботу'
    

    def get_inlines(self, request, obj):
        return super().get_inlines(request, obj)
    
    # inlines = [
    #     inlines.WfDFXVersionControlLogInline,
    #     inlines.WfCutLogInline,
    #     inlines.WfBendLogInline,
    #     inlines.WfWeldLogInline,
    #     inlines.WfLocksmithLogInline,
    #     inlines.WfGlassLogInline,
    #     inlines.WfQualityControlLogInline,
    #     inlines.WfFinalProductLogInline,
    # ]
    
    list_display = [
        '_priority',
        
        'model',
        'configuration',
        'fireclay_type',
        'glazing_type',
        'frame_type',
        
        'note',
        
        'payment',
        
        'start_manufacturing',
        '_start_date',
        'deadline_date',
    ]
    
    list_display_links = ['model', 'configuration', 'fireclay_type',]
    
    list_filter = ['model', 'configuration', 'fireclay_type', 'glazing_type', 'priority',]
        
    list_select_related = [
        'model',
        'configuration',
        'fireclay_type',
        'glazing_type',
        'frame_type',
        'priority',
        'payment',
    ]
    
    search_fields = [
        'model__name',
        'configuration__name',
    ]
    
    fieldsets = (
        (None, {
        'fields': (
            ('model', 'configuration', 'fireclay_type', 'glazing_type', 'frame_type', 'priority',),
            ('note',),
            'delivery', 'mobile_number', 'email', 'payment',
            'start_manufacturing', 'deadline_date',
            ),
        'classes': ('wide', 'extrapretty'),
        }),
    )
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'20'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }
    

admin.site.site_header = 'Gavryliv&Sons'
admin.site.index_title = 'Адміністрація'

admin.site.register(core_models.WfModelList, WfModelListAdmin)
admin.site.register(core_models.WfJobStatusList, WfJobStatusListAdmin)
admin.site.register(core_models.WfConfigurationList, WfConfigurationListAdmin)
admin.site.register(core_models.WfFireclayTypeList, WfFireclayTypeListAdmin)
admin.site.register(core_models.WfFrameTypeList, WfFrameTypeListAdmin)
admin.site.register(core_models.WfGlazingTypeList, WfGlazingTypeListAdmin)
admin.site.register(core_models.WfPriorityList, WfPriorityListAdmin)
admin.site.register(core_models.WfPaymentList, WfPaymentListAdmin)
admin.site.register(core_models.WfDFXVersionControlLog, WfDFXVersionControlLogAdmin)
admin.site.register(core_models.WfOrderLog, WfOrderLogAdmin)
