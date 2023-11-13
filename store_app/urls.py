from .views_api import CategoryCreateList
from django.urls import path


urlpatterns = [
    path('category/', CategoryCreateList.as_view(), name="category_list_create_api"),
    # path('task/<int:pk>/', TaskUpdateDetailRemove.as_view(), name="task_update_detail_remove_api"),
    # path('tasks_list/', TasksListCreateList.as_view(), name="tasks_list_list_create_api"),
    # path('tasks_list/<int:pk>/', TasksListUpdateDetailRemove.as_view(),
    #      name="tasks_list_update_detail_remove_api"),
    # path('tasks_list/<int:pk>/task/', TaskCreateList.as_view(), name="task_list_create_grouped_api"),
    # path('tasks_list/<int:pk>/task/<int:task_pk>/', TaskUpdateDetailRemove.as_view(),
    #      name="task_update_detail_remove_grouped_api"),
]
