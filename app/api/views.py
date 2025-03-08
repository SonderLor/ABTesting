import hashlib

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from app.tasks import log_event_task
from experiments.models import Experiment, UserGroup
from .serializers import ExperimentSerializer, UserGroupSerializer


class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['GET'], url_path='assign-group')
    def assign_group(self, request, pk=None):
        user_id = request.query_params.get('user_id')
        experiment = self.get_object()

        hash_value = hashlib.md5(
            f"{user_id}_{experiment.id}".encode()
        ).hexdigest()
        hash_int = int(hash_value, 16) % 100

        cumulative = 0
        for group, ratio in experiment.group_ratio.items():
            cumulative += ratio
            if hash_int < cumulative:
                selected_group = group
                break

        UserGroup.objects.update_or_create(
            user_id=user_id,
            experiment=experiment,
            defaults={'group': selected_group}
        )

        return Response({'group': selected_group})


class UserGroupViewSet(viewsets.ModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        experiment_id = self.request.query_params.get('experiment_id')
        if experiment_id:
            return UserGroup.objects.filter(experiment_id=experiment_id)
        return super().get_queryset()


class EventLogView(APIView):
    def post(self, request):
        event_data = request.data
        log_event_task.delay(event_data)
        return Response({'status': 'accepted'}, status=202)
