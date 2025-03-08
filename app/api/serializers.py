from rest_framework import serializers
from experiments.models import Experiment, UserGroup, Event


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True},
            'status': {'read_only': True},
            'start_date': {'read_only': True},
        }

    def validate_group_ratio(self, value):
        if sum(value.values()) != 100:
            raise serializers.ValidationError(
                "Сумма значений group_ratio должна быть 100%."
            )
        return value


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = '__all__'
        extra_kwargs = {
            'user_id': {'required': True},
            'experiment': {'required': True},
        }


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {
            'user_id': {'required': True},
            'event_type': {'required': True},
            'experiment': {'required': True},
        }
