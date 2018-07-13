from django.contrib.auth import get_user_model

from rest_framework import serializers

from django_celery_results.models import TaskResult

from robots.models import TaskRun, RSeoStatus

User = get_user_model()


class TaskResultSerializer(serializers.HyperlinkedModelSerializer):
    result = serializers.HyperlinkedIdentityField(view_name='robots:task_result_detail',
                                                  lookup_field='task_id',
                                                  lookup_url_kwarg='task_id'
                                                  )
    task_id = serializers.ReadOnlyField()

    class Meta:
        model = TaskResult
        fields = (
            'task_id',
            'status',
            'result',
            'date_done',
        )


class TaskResultStatusSerializer(serializers.ModelSerializer):
    task_id = serializers.ReadOnlyField()

    class Meta:
        model = TaskResult
        fields = (
            'task_id',
            'result',
            'meta',
        )


class TaskRunSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    task_id = serializers.ReadOnlyField()

    status = serializers.HyperlinkedIdentityField(view_name='robots:task_execution_detail',
                                                  lookup_field='task_id',
                                                  lookup_url_kwarg='task_id'
                                                  )

    class Meta:
        model = TaskRun
        fields = (
            'id',
            'task_id',
            'status',
        )


class TaskRunStateSerializer(serializers.ModelSerializer):
    task_id = serializers.ReadOnlyField()

    class Meta:
        model = TaskRun
        fields = (
            'task_id',
            'status',
            'task_environment',
        )


class UserNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'last_name',
            'email'
        )


class RSeoSerializer(serializers.ModelSerializer):

    owner = UserNameSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    execute = serializers.HyperlinkedIdentityField(view_name='robots:start_robot',
                                                   lookup_field='id',
                                                   lookup_url_kwarg='pk')

    class Meta:
        model = RSeoStatus
        fields = (
            "id",
            "domain",
            "google",
            "yahoo",
            "bing",
            "duckduck",
            "destination",
            "owner",
            "execute",
        )
