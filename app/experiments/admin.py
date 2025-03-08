from django.contrib import admin
from django.utils.html import format_html
from .models import Experiment, UserGroup, Event, ABMetric


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_by", "start_date", "end_date", "group_ratio_display")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("name", "created_by__username")
    readonly_fields = ("start_date",)
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "status", "created_by", "group_ratio", "target_metrics", "start_date", "end_date")
        }),
    )

    def group_ratio_display(self, obj):
        return format_html("<pre>{}</pre>", obj.group_ratio)
    group_ratio_display.short_description = "Group Ratio"


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ("user_id", "experiment", "group")
    list_filter = ("experiment", "group")
    search_fields = ("user_id", "experiment__name")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("experiment", "user_id", "event_type", "timestamp")
    list_filter = ("event_type", "experiment")
    search_fields = ("user_id", "experiment__name", "event_type")
    ordering = ("-timestamp",)


@admin.register(ABMetric)
class ABMetricAdmin(admin.ModelAdmin):
    list_display = ("experiment", "group", "ctr", "conversion", "p_value", "timestamp")
    list_filter = ("experiment", "group")
    search_fields = ("experiment__name", "group")
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp",)