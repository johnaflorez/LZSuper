from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from rest_framework.viewsets import ViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated


from robots.tasks import google, duck, yahoo, bing, sendmail

from celery import  chord

from robots.models import RSeoStatus, TaskRun
from robots.api.serializers import (TaskResultSerializer, TaskResultStatusSerializer,

                                    TaskRunSerializer, TaskRunStateSerializer,
                                    RSeoSerializer)
from robots.api.permissions import IsOwnerOrReadOnly

from django_celery_results.models import TaskResult


class TaskResultViewSet(ViewSet):


    permission_classes = (IsAuthenticated, )

    def list(self, request):
        results = TaskResult.objects.all()
        serializer = TaskResultSerializer(results,
                                          context={'request': request},
                                          many=True
                                          )
        return JsonResponse(serializer.data, safe=False, status=200)

    def retrieve(self, request, task_id):
        try:
            result = TaskResult.objects.get(task_id=task_id)
        except ObjectDoesNotExist:
            raise ValidationError(detail='Task don\'t found')
        else:
            serializer = TaskResultStatusSerializer(result,
                                                    context={'request': request}
                                                    )
            return JsonResponse(serializer.data, status=200)


task_result_list = TaskResultViewSet.as_view(
    {'get': 'list'}
)

task_result_detail = TaskResultViewSet.as_view(
    {'get': 'retrieve'}
)


class TaskOptions(ViewSet):

    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated,)

    def create(self, request, *args, **kwargs):

        run_status = request.data.pop('start', None)

        try:
            RSeoStatus.objects.create(owner=request.user, **request.data).save()
        except IntegrityError:
            raise ValidationError("RSeo Information mal formed")
        else:
            if run_status:
                tasks_exec = (google, yahoo, bing, duck,)

                browser_nav = list(filter(lambda x: request.data[x] is True, ('google',
                                                                              'yahoo',
                                                                              'duckduck',
                                                                              'bing',)
                                          )
                                   )

                chord((task.s(keyword=request.data['keyword']) for task in tasks_exec if task.name in browser_nav)) \
                    (sendmail.s())

        return JsonResponse({'message': 'Task Save successfully'})

    def list(self, request):
        tasks = TaskRun.objects.all()
        serializer = TaskRunSerializer(tasks,
                                       context={'request': request},
                                       many=True)
        return JsonResponse(serializer.data, status=200, safe=False)

    def status(self, request, task_id):
        try:
            task = TaskRun.objects.get(task_id=task_id)
        except ObjectDoesNotExist:
            raise ValidationError(detail='Task not found')
        else:
            serializer = TaskRunStateSerializer(task, context={'request': request})
            return JsonResponse(serializer.data, status=200)


run_task = TaskOptions.as_view(
    {'post': 'create'}
)

task_execution_list = TaskOptions.as_view(
    {'get': 'list'}
)

task_execution_detail = TaskOptions.as_view(
    {'get': 'status'}
)


class RobotsViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        robots = RSeoStatus.objects.all()
        serializer = RSeoSerializer(robots,
                                    many=True,
                                    context={'request': request}
                                    )
        return JsonResponse(serializer.data, status=200, safe=False)

    def start(self, request, pk, *args, **kwargs):
        try:
            robot_info = RSeoStatus.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise ValidationError("Robot don't exist")
        else:

            tasks_exec = (google, yahoo, bing, duck,)

            robot_dict = robot_info.as_dict()

            browser_nav = list(filter(lambda x: robot_dict[x] is True, ('google',
                                                                        'yahoo',
                                                                        'duckduck',
                                                                        'bing',)
                                      )
                               )

            chord(
                (task.s(keyword=robot_dict['keyword']) for task in tasks_exec if task.name in browser_nav)
            )(sendmail.s())

            return JsonResponse({'message': 'Task Send to execute successfully'})


list_robots = RobotsViewSet.as_view(
    {'get': 'list'}
)

start_robot = RobotsViewSet.as_view(
    {'post': 'start'}
)
