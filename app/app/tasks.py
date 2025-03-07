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
            views = experiment.events.filter(
                event_type='view',
                group=group.group
            ).count()
            clicks = experiment.events.filter(
                event_type='click',
                group=group.group
            ).count()

            """ CTR (Click-Through Rate)
                Процент пользователей, которые кликнули на элемент,
                относительно общего числа пользователей, увидевших его.
            """
            ctr = (clicks / views) * 100 if views > 0 else 0
            groups_data[group.group] = {'ctr': ctr}

        group_a_data = [
            1 if e.event_type == 'click' else 0
            for e in experiment.events.filter(group='A')
        ]
        group_b_data = [
            1 if e.event_type == 'click' else 0
            for e in experiment.events.filter(group='B')
        ]

        """ P-value (Статистическая значимость)
            Вероятность того, что различия между группами A и B случайны.
            Если p_value < 0.05, различия считаются значимыми.
        """
        t_stat, p_value = stats.ttest_ind(group_a_data, group_b_data)

        for group, data in groups_data.items():
            ABMetric.objects.create(
                experiment=experiment,
                group=group,
                ctr=data['ctr'],
                p_value=p_value if group == 'A' else None,
                timestamp=timezone.now()
            )
