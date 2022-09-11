from this import d
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



class WfWorkStageListAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'name',
    ]

    list_display_links = ['name',]

    search_fields = [
        'name',
    ]



class WfAuthUserGroupAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        '_stage',
    ]

    list_display_links = ['user',]

    list_select_related = [
        'user',
        'stage',
    ]

    search_fields = [
        'user', 'stage',
    ]

    list_filter = [
        'user',
        'stage__description',
    ]



class OrderAdmin(admin.ModelAdmin):

    actions = ['send_to_work', ] # 'pass_work',

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


    def send_to_work(self, request, queryset):
        try:
            for order in queryset:
                order.start_manufacturing = True
                order.save()

            self.message_user(request, ngettext(
                '%d замовлення було відправлено в роботу!',
                '%d замовлень було відправлено в роботу!',
                len(queryset),
            ) % len(queryset), messages.SUCCESS)

        except Exception as e:
            self.message_user(request, e, messages.ERROR)


    def pass_work(self, request, queryset):
        try:
            orders_passed = 0
            for order in queryset:
                order = core_models.Order.objects.filter(models.Q(id=order.id) &
                                                              models.Q(dxf_logs__isnull=False) & models.Q(dxf_logs__stage__id=2) & models.Q(dxf_logs__status__id=1) &
                                                              models.Q(cut_logs__isnull=False) & models.Q(cut_logs__stage__id=2) & models.Q(dxf_logs__status__id=1) &
                                                              models.Q(bend_logs__isnull=False) & models.Q(bend_logs__stage__id=2) & models.Q(dxf_logs__status__id=1) &
                                                              models.Q(weld_logs__isnull=False) & models.Q(weld_logs__stage__id=2) & models.Q(dxf_logs__status__id=1) &
                                                              models.Q(locksmith_logs__isnull=False) & models.Q(locksmith_logs__stage__id=2) & models.Q(dxf_logs__status__id=1))

                if order:
                    orders_passed += 1
                    core_models.WfGlassLog.create(order=order, stage=None)

            self.message_user(request, ngettext(
                '%d напівфабрикат погоджено!',
                '%d напівфабрикатів погоджено!',
                orders_passed,
            ) % orders_passed, messages.SUCCESS)

        except Exception as e:
            self.message_user(request, e, messages.ERROR)

    send_to_work.short_description = 'Відправити в роботу'
    pass_work.short_description = 'Погодити напівфабрикат'

    inlines = [
        inlines.OrderWorkStageInline,
    ]

    list_display = [
        '_priority',

        'model',
        'configuration',
        'fireclay_type',
        'glazing_type',
        'frame_type',

        'payment',

        'start_manufacturing',
        'semifinished_ready',
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
            'delivery', 'mobile_number', 'email', 'payment',
            'start_manufacturing', 'deadline_date'
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
admin.site.register(core_models.WfWorkStageList, WfWorkStageListAdmin)
admin.site.register(core_models.WfAuthUserGroup, WfAuthUserGroupAdmin)
admin.site.register(core_models.Order, OrderAdmin)
