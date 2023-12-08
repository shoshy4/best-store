import pytest
from tests.factory.product import TasksListFactory


@pytest.fixture
def taskslist_1(user2):
    taskslist = TasksListFactory(owner=user2)
    taskslist.id = 1
    taskslist.save()
    return taskslist


@pytest.fixture
def taskslist():
    taskslist = TasksListFactory()
    return taskslist


@pytest.fixture
def taskslist2(user2):
    taskslist = TasksListFactory(owner=user2)
    return taskslist


@pytest.fixture
def taskslists(user2):
    taskslists = []
    for i in range(4):
        task = TasksListFactory(owner=user2)
        taskslists.append(task)
    return taskslists
