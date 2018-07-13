from django.conf.urls import url

from robots.views import (task_result_list, task_result_detail,
                          run_task, task_execution_list, task_execution_detail,
                          list_robots, start_robot
                          )

app_name = 'robots'
urlpatterns = [
    url(r'^task/$', task_execution_list, name='task_execution_list'),
    url(r'^task/(?P<task_id>(\w+|[-]+)+)/$', task_execution_detail, name='task_execution_detail'),
    url(r'^tasks_done/$', task_result_list, name='task_result_list'),
    url(r'^tasks_done/(?P<task_id>(\w+|[-]+)+)/$', task_result_detail, name='task_result_detail'),
    url(r'^robot/create/$', run_task, name='create_robot'),
    url(r'^robots/$', list_robots, name='list_robots'),
    url(r'robot/(?P<pk>\d+)/$', start_robot, name='start_robot')
]

