from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_group_ratio(value):
    """Проверка, что сумма значений в group_ratio равна 100%."""
    if sum(value.values()) != 100:
        raise ValidationError("Сумма значений в group_ratio должна быть 100%.")


class Experiment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=200, unique=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Создатель"
    )
    group_ratio = models.JSONField(
        default={"A": 50, "B": 50},
        validators=[validate_group_ratio]
    )
    target_metrics = models.JSONField(
        default=list
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class UserGroup(models.Model):
    user_id = models.CharField(max_length=100)
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='user_groups'
    )
    group = models.CharField(max_length=10)

    class Meta:
        unique_together = ['user_id', 'experiment']

    def __str__(self):
        return f"{self.user_id} | {self.experiment.name} | {self.group}"


class Event(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='events'
    )
    user_id = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)


class ABMetric(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    group = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=timezone.now)
    ctr = models.FloatField(default=0.0)
    conversion = models.FloatField(default=0.0)
    p_value = models.FloatField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['experiment', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.experiment.name} | {self.group} | {self.timestamp}"
