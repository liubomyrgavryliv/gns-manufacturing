from django.db.models import Q, OuterRef, Case, When, Value

from .models.core import WfOrderLog


def annotate_current_stage():
    
    return WfOrderLog.objects.filter(Q(dxf_logs__isnull=False) & Q(dxf_logs__stage__id=2) & Q(dxf_logs__status__id=1) |
                                        Q(cut_logs__isnull=False) & Q(cut_logs__stage__id=2) & Q(dxf_logs__status__id=1) |
                                        Q(bend_logs__isnull=False) & Q(bend_logs__stage__id=2) & Q(dxf_logs__status__id=1) |
                                        Q(weld_logs__isnull=False) & Q(weld_logs__stage__id=2) & Q(dxf_logs__status__id=1) |
                                        Q(locksmith_logs__isnull=False) & Q(locksmith_logs__stage__id=2) & Q(dxf_logs__status__id=1) |
                                        Q(glass_logs__isnull=False) & Q(glass_logs__stage__id=2) & Q(glass_logs__status__id=1) |
                                        Q(quality_logs__isnull=False) & Q(quality_logs__stage__id=2) & Q(quality_logs__status__id=1) |
                                        Q(final_logs__isnull=False) & Q(final_logs__stage__id=2) & Q(final_logs__status__id=1)
                              ) \
                             .annotate(current_stage=Case(
                                When(Q(final_logs__isnull=False) & Q(final_logs__stage__id=2) & Q(final_logs__status__id=1), then=Value('Фінальний продукт')),
                                When(Q(quality_logs__isnull=False) & Q(quality_logs__stage__id=2) & Q(quality_logs__status__id=1), then=Value('Контроль якості')),
                                When(Q(glass_logs__isnull=False) & Q(glass_logs__stage__id=2) & Q(glass_logs__status__id=1), then=Value('Скління')),
                                When(Q(locksmith_logs__isnull=False) & Q(locksmith_logs__stage__id=2) & Q(dxf_logs__status__id=1), then=Value('Слюсарські роботи')),
                                When(Q(weld_logs__isnull=False) & Q(weld_logs__stage__id=2) & Q(dxf_logs__status__id=1), then=Value('Зварювання')),
                                When(Q(bend_logs__isnull=False) & Q(bend_logs__stage__id=2) & Q(dxf_logs__status__id=1), then=Value('Гнуття')),
                                When(Q(cut_logs__isnull=False) & Q(cut_logs__stage__id=2) & Q(dxf_logs__status__id=1), then=Value('Порізка')),
                                When(Q(dxf_logs__isnull=False) & Q(dxf_logs__stage__id=2) & Q(dxf_logs__status__id=1), then=Value('Перевірка DXF версій')),
                                default=Value('Очікує виконання')
                            ))