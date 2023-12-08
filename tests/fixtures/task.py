import pytest
from tests.factory.category import TaskFactory
from datetime import datetime


@pytest.fixture
def task():
    task = TaskFactory()
    return task


@pytest.fixture
def task2(user2):
    task = TaskFactory(owner=user2)
    return task


@pytest.fixture
def task_group(taskslist_1, user2):
    task = TaskFactory(owner=user2, task_list=taskslist_1)
    return task


@pytest.fixture
def tasks_group(taskslist_1, user2):
    tasks = []
    for ix in range(4):
        task = TaskFactory(task_list=taskslist_1, owner=user2)
        tasks.append(task)
    return tasks


@pytest.fixture
def tasks(user2):
    tasks = []
    for i in range(4):
        task = TaskFactory(owner=user2)
        tasks.append(task)
    return tasks
