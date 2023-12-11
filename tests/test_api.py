from django.urls import reverse
import pytest


@pytest.mark.django_db
def test_sign_up(api_client_unauth):
    url = reverse('sign_up')
    client, _ = api_client_unauth
    payload = {"username": "me",
               "password": "me12345!",
               "confirm_password": "me12345!"
               }
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    assert "id" in response.data


@pytest.mark.django_db
def test_task_list(api_client_auth, tasks):
    url = reverse('task_list_create_api')
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 4


@pytest.mark.django_db
def test_task_list_grouped(api_client_auth, tasks_group, taskslist_1):
    url = reverse('task_list_create_grouped_api', kwargs={'pk': taskslist_1.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 4


@pytest.mark.django_db
def test_task_create(api_client_auth):
    url = reverse('task_list_create_api')
    client, _ = api_client_auth
    payload = {"title": "A new task",
               "description": "Just a new task. trying",
               "status": "finished",
               "owner": 1
               }
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    assert "title" in response.data


@pytest.mark.django_db
def test_task_create_grouped(api_client_auth, tasks_group, taskslist_1):
    url = reverse('task_list_create_grouped_api', kwargs={'pk': taskslist_1.id})
    client, _ = api_client_auth
    payload = {"title": "A new task",
               "description": "Just a new task. trying",
               "status": "finished",
               "owner": 1
               }
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    assert "title" in response.data


@pytest.mark.django_db
def test_task_detail(api_client_auth, task2):
    url = reverse('task_update_detail_remove_api', kwargs={'pk': task2.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert "title" in response.data


@pytest.mark.django_db
def test_task_detail_grouped(api_client_auth, task_group, taskslist_1):
    url = reverse('task_update_detail_remove_grouped_api', kwargs={'task_pk': task_group.id, 'pk': taskslist_1.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert "title" in response.data


@pytest.mark.django_db
def test_task_update(api_client_auth, task2):
    url = reverse('task_update_detail_remove_api', kwargs={'pk': task2.id})
    client, _ = api_client_auth
    response = client.patch(url, {
        "title": "A new task",
        "description": "Just a new task. trying",
        "status": "pending"}, format='json')
    assert response.status_code == 200
    assert response.data["title"] == "A new task"


@pytest.mark.django_db
def test_task_update_grouped(api_client_auth, task_group, taskslist_1):
    url = reverse('task_update_detail_remove_grouped_api', kwargs={'task_pk': task_group.id, 'pk': taskslist_1.id})
    client, _ = api_client_auth
    response = client.patch(url, {
        "title": "A new task",
        "description": "Just a new task. trying",
        "status": "pending"}, format='json')
    assert response.status_code == 200
    assert response.data["title"] == "A new task"


@pytest.mark.django_db
def test_task_delete(api_client_auth, task2):
    url = reverse('task_update_detail_remove_api', kwargs={'pk': task2.id})
    client, _ = api_client_auth
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_task_delete_grouped(api_client_auth, task_group, taskslist_1):
    url = reverse('task_update_detail_remove_grouped_api', kwargs={'task_pk': task_group.id, 'pk': taskslist_1.id})
    client, _ = api_client_auth
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_tasks_list_list(api_client_auth, taskslists):
    url = reverse('tasks_list_list_create_api')
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 4


@pytest.mark.django_db
def test_tasks_list_create(api_client_auth, taskslist2):
    url = reverse('tasks_list_list_create_api')
    client, _ = api_client_auth
    payload = {"title": "New tasks list"}
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    assert "title" in response.data


@pytest.mark.django_db
def test_tasks_list_detail(api_client_auth, taskslist2):
    url = reverse('tasks_list_update_detail_remove_api', kwargs={'pk': taskslist2.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert "title" in response.data


@pytest.mark.django_db
def test_tasks_list_update(api_client_auth, taskslist2):
    url = reverse('tasks_list_update_detail_remove_api', kwargs={'pk': taskslist2.id})
    client, _ = api_client_auth
    response = client.patch(url, {"title": "A list of new tasks"}, format='json')
    assert response.status_code == 200
    assert response.data["title"] == "A list of new tasks"


@pytest.mark.django_db
def test_tasks_list_delete(api_client_auth, taskslist2):
    url = reverse('tasks_list_update_detail_remove_api', kwargs={'pk': taskslist2.id})
    client, _ = api_client_auth
    response = client.delete(url)
    assert response.status_code == 204
