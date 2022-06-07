from django.db.models import Q, OuterRef, Case, When, Value, Exists, Max, Subquery

from .models.core import WfCutLog, WfOrderLog, WfFinalProductLog, WfLocksmithLog, WfGlassLog, WfBendLog, \
WfDXFVersionControlLog, WfWeldLog, WfQualityControlLog


def annotate_current_stage():
    
    return WfOrderLog.objects.annotate(
                                 current_stage=Case(
                                    When(Exists(WfFinalProductLog.objects.filter(Q(stage__id=2) & Q(status__id=1) & Q(order=OuterRef('id')))), then=Value('Фінальний продукт')),
                                    When(Exists(WfQualityControlLog.objects.filter(Q(stage__id=2) & Q(status__id=1) & Q(order=OuterRef('id')))), then=Value('Контроль якості')),
                                    When(Exists(WfGlassLog.objects.filter(Q(stage__id=2) & Q(status__id=1) & Q(order=OuterRef('id')))), then=Value('Скління')),
                                    When(Exists(WfLocksmithLog.objects.filter(Q(stage__id=2) & Q(status__id=1) & Q(order=OuterRef('id')))), then=Value('Слюсарські роботи')),
                                    When(Exists(WfWeldLog.objects.filter(Q(stage__id=2) & Q(status__id=1) & Q(order=OuterRef('id')))), then=Value('Зварювання')),
                                    When(Exists(WfBendLog.objects.filter(Q(stage__id=2) & Q(status__id=1) & Q(order=OuterRef('id')))), then=Value('Гнуття')),
                                    When(Exists(WfCutLog.objects.filter(Q(stage__id=2) & Q(status__id=1) & Q(order=OuterRef('id')))), then=Value('Порізка')),
                                    When(Exists(WfDXFVersionControlLog.objects.filter(Q(stage__id=2) & Q(status__id=1) & Q(order=OuterRef('id')))), then=Value('Перевірка DXF версій')),
                                    default=Value('Очікує виконання')
                                 )
                                )
