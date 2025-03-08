from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExperimentViewSet, UserGroupViewSet, EventLogView, EventViewSet

router = DefaultRouter()
router.register(r'experiments', ExperimentViewSet, basename='experiments')
router.register(r'user-groups', UserGroupViewSet, basename='user-groups')
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('', include(router.urls)),
    path('log-event/', EventLogView.as_view(), name='log-event'),
]
