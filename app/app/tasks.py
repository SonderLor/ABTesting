from celery import shared_task
from django.conf import settings
from scipy import stats
from django.utils import timezone
import logging

from experiments.models import Experiment, ABMetric

logger = logging.getLogger(__name__)


@shared_task
def log_event_task(event_data):
    try:
        settings.MONGO_DB.events.insert_one(event_data)
        logger.info(f"Событие записано: {event_data}")
    except Exception as e:
        logger.error(f"Ошибка записи в MongoDB: {e}")


@shared_task
def calculate_metrics():
    experiments = Experiment.objects.filter(
        status="active"
    ).prefetch_related('user_groups')

    for experiment in experiments:
        groups_data = {}
        for group in experiment.user_groups.all():
            user_ids = experiment.user_groups.filter(
                group=group.group
            ).values_list('user_id', flat=True)

            views = experiment.events.filter(event_type='view', user_id__in=user_ids).count()
            clicks = experiment.events.filter(event_type='click', user_id__in=user_ids).count()

            ctr = (clicks / views) * 100 if views > 0 else 0
            groups_data[group.group] = {'ctr': ctr}

        group_a_data = [
            1 if e.event_type == 'click' else 0
            for e in experiment.events.filter(
                user_id__in=experiment.user_groups.filter(
                    group='A'
                ).values_list('user_id', flat=True)
            )
        ]
        group_b_data = [
            1 if e.event_type == 'click' else 0
            for e in experiment.events.filter(
                user_id__in=experiment.user_groups.filter(
                    group='B'
                ).values_list('user_id', flat=True)
            )
        ]

        if group_a_data and group_b_data:
            t_stat, p_value = stats.ttest_ind(group_a_data, group_b_data, equal_var=False)
        else:
            p_value = None

        for group, data in groups_data.items():
            ABMetric.objects.create(
                experiment=experiment,
                group=group,
                ctr=data['ctr'],
                p_value=p_value if group == 'A' else None,
                timestamp=timezone.now()
            )
