from decimal import Decimal

from django.urls import reverse
import pytest

from store_app.models import Order

IN_PROCESS = 1
NOT_COMPLETED = 2
PAID = 3
SENT = 4
DELIVERED = 5
RECEIVED = 6
ORDER_STATUS_CHOICES = (
    (IN_PROCESS, "Completed. Payment in process"),
    (NOT_COMPLETED, "Not completed yet. Make sure payment_details and shipping_address are added"),
    (PAID, "Paid. In process"),
    (SENT, "Sent to customer's shipping address"),
    (DELIVERED, "Delivered"),
    (RECEIVED, "Received")
)


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
def test_category_list(api_client_auth, categories):
    url = reverse('category_list_create_api')
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 4


@pytest.mark.django_db
def test_category_user_create(api_client_auth):
    url = reverse('category_list_create_api')
    client, _ = api_client_auth
    payload = {"name": "fruits"}
    response = client.post(url, payload, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_category_create(api_client_admin):
    url = reverse('category_list_create_api')
    client, _ = api_client_admin
    payload = {"name": "fruits"}
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    assert "name" in response.data


@pytest.mark.django_db
def test_category_update(api_client_admin, category1):
    url = reverse('category_update_detail_remove_api', kwargs={'pk': category1.id})
    client, _ = api_client_admin
    response = client.patch(url, {"name": "vegetables"}, format='json')
    assert response.status_code == 200
    assert response.data["name"] == "vegetables"


@pytest.mark.django_db
def test_category_detail(api_client_admin, category1):
    url = reverse('category_update_detail_remove_api', kwargs={'pk': category1.id})
    client, _ = api_client_admin
    response = client.get(url)
    assert response.status_code == 200
    assert "name" in response.data


@pytest.mark.django_db
def test_category_delete(api_client_admin, category1):
    url = reverse('category_update_detail_remove_api', kwargs={'pk': category1.id})
    client, _ = api_client_admin
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_product_list(api_client_auth, products):
    url = reverse('product_list_create_api')
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 4


@pytest.mark.django_db
def test_product_user_create(api_client_admin, category):
    url = reverse('product_list_create_api')
    client, _ = api_client_admin
    payload = {"name": "fruits",
               "description": "",
               "price": "",
               "amount_in_stock": "",
               "category": category.id}
    response = client.post(url, payload, format='json')
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_user_create(api_client_auth, category):
    url = reverse('product_list_create_api')
    client, _ = api_client_auth
    payload = {"name": "Kiwi",
               "description": "Green kiwi fruit",
               "price": 6.90,
               "amount_in_stock": 100,
               "category": category.id}
    response = client.post(url, payload, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_product_update(api_client_admin, product):
    url = reverse('product_update_detail_remove_api', kwargs={'pk': product.id})
    client, _ = api_client_admin
    response = client.patch(url, {"price": 8.90}, format='json')
    assert response.status_code == 200
    assert Decimal(response.data["price"]) == Decimal('8.90')


@pytest.mark.django_db
def test_product_detail(api_client_unauth, product):
    url = reverse('product_update_detail_remove_api', kwargs={'pk': product.id})
    client, _ = api_client_unauth
    response = client.get(url)
    assert response.status_code == 200
    assert "name" in response.data


@pytest.mark.django_db
def test_product_user_delete(api_client_auth, product):
    url = reverse('product_update_detail_remove_api', kwargs={'pk': product.id})
    client, _ = api_client_auth
    response = client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_product_delete(api_client_admin, product):
    url = reverse('product_update_detail_remove_api', kwargs={'pk': product.id})
    client, _ = api_client_admin
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_feedback_list(api_client_auth, feedbacks, product):
    url = reverse('feedback_list_create_api', kwargs={'pk': product.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_feedback_wrong_user_create(api_client_user, product):
    url = reverse('feedback_list_create_api', kwargs={'pk': product.id})
    client, _ = api_client_user
    payload = {"product": product.id,
               "rate": 4,
               "text": "tasty"}
    response = client.post(url, payload, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_feedback_user_create(api_client_auth, product):
    url = reverse('feedback_list_create_api', kwargs={'pk': product.id})
    client, _ = api_client_auth
    payload = {"rate": 5,
               "text": "delicious"}
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    assert "rate" in response.data


@pytest.mark.django_db
def test_feedback_update(api_client_auth, feedback, product):
    url = reverse('feedback_update_detail_remove_api', kwargs={'feedback_pk': feedback.id, 'pk': product.id})
    client, _ = api_client_auth
    payload = {"product": product.id,
               "rate": 4,
               "text": "tasty"}
    response = client.put(url, payload, format='json')
    assert response.status_code == 200
    assert response.data["text"] == "tasty"


@pytest.mark.django_db
def test_feedback_detail(api_client_user, feedback, product):
    url = reverse('feedback_update_detail_remove_api', kwargs={'feedback_pk': feedback.id, 'pk': product.id})
    client, _ = api_client_user
    response = client.get(url)
    assert response.status_code == 400


@pytest.mark.django_db
def test_feedback_detail(api_client_auth, feedback, product):
    url = reverse('feedback_update_detail_remove_api', kwargs={'feedback_pk': feedback.id, 'pk': product.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert "rate" in response.data


@pytest.mark.django_db
def test_feedback_delete(api_client_auth, feedback, product):
    url = reverse('feedback_update_detail_remove_api', kwargs={'feedback_pk': feedback.id, 'pk': product.id})
    client, _ = api_client_auth
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_orders_user(api_client_auth, orders):
    url = reverse('order_list_api')
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_orders(api_client_admin, orders):
    url = reverse('order_list_api')
    client, _ = api_client_admin
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_cart_item_create(api_client_auth, product, cart):
    url = reverse('item_create_list_remove_api')
    client, _ = api_client_auth
    payload = {"product": product.id,
               "amount": 5}
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    assert "amount" in response.data


@pytest.mark.django_db
def test_cart_item_list(api_client_auth, cart):
    url = reverse('item_create_list_remove_api')
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 2


@pytest.mark.django_db
def test_cart_item_unauth_update(api_client_unauth, cart_item, product, cart):
    url = reverse('item_update_detail_remove_api', kwargs={'pk': cart_item.id})
    client, _ = api_client_unauth
    response = client.patch(url, {"amount": 8}, format='json')
    assert response.status_code == 401


@pytest.mark.django_db
def test_cart_item_update(api_client_auth, cart_item, product, cart):
    url = reverse('item_update_detail_remove_api', kwargs={'pk': cart_item.id})
    client, _ = api_client_auth
    response = client.patch(url, {"amount": 8}, format='json')
    assert response.status_code == 200
    assert response.data["amount"] == 8


@pytest.mark.django_db
def test_cart_item_detail(api_client_auth, cart_item):
    url = reverse('item_update_detail_remove_api', kwargs={'pk': cart_item.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert "amount" in response.data


@pytest.mark.django_db
def test_cart_item_delete(api_client_auth, cart_item):
    url = reverse('item_update_detail_remove_api', kwargs={'pk': cart_item.id})
    client, _ = api_client_auth
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_order_list(api_client_auth, orders):
    url = reverse('order_list_create_api')
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 4


@pytest.mark.django_db
def test_order_create(api_client_auth, user2, cart_filled, shipping_address, payment_details):
    url = reverse('order_list_create_api')
    client, _ = api_client_auth
    payload = {"payment_details": payment_details.id}
    response = client.post(url, payload, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_order_update(api_client_auth, order, shipping_address2):
    url = reverse('order_update_detail_remove_api', kwargs={'pk': order.id})
    client, _ = api_client_auth
    payload = {"shipping_address": shipping_address2.id}
    response = client.patch(url, payload, format='json')
    assert response.status_code == 200
    assert "shipping_address" in response.data


@pytest.mark.django_db
def test_order_detail(api_client_auth, order):
    url = reverse('order_update_detail_remove_api', kwargs={'pk': order.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert "order_status" in response.data


@pytest.mark.django_db
def test_order_delete(api_client_auth, order):
    url = reverse('order_update_detail_remove_api', kwargs={'pk': order.id})
    client, _ = api_client_auth
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_order_change_status(api_client_admin, order):
    url = reverse('order_update_detail_remove_api', kwargs={'pk': order.id})
    client, _ = api_client_admin
    payload = {"orders_status": Order.IN_PROCESS}
    response = client.patch(url, payload, format='json')
    assert response.status_code == 200
    assert "order_status" in response.data


@pytest.mark.django_db
def test_order_receiving(api_client_auth, order):
    url = reverse('order_receiving_api', kwargs={'pk': order.id})
    client, _ = api_client_auth
    response = client.patch(url, format='json')
    assert response.status_code == 200
    assert "order_status" in response.data


@pytest.mark.django_db
def test_order_user_receiving(api_client_user, order):
    url = reverse('order_receiving_api', kwargs={'pk': order.id})
    client, _ = api_client_user
    response = client.patch(url, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_order_payment(api_client_auth, order_processed, cart_filled):
    url = reverse('order_payment_api', kwargs={'pk': order_processed.id})
    client, _ = api_client_auth
    response = client.post(url, format='json')
    assert response.status_code == 200


@pytest.mark.django_db
def test_payment_details_list(api_client_auth, few_payment_details):
    url = reverse('payment_details_list_create_api')
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_payment_details_create(api_client_auth, user2):
    url = reverse('payment_details_list_create_api')
    client, _ = api_client_auth
    payload = {"card_number": "5678497893234567",
               "cvv": "356",
               "expiration_date": "2026-02-12",
               "customer": user2.id}
    response = client.post(url, payload, format='json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_payment_details_update(api_client_auth, payment_details):
    url = reverse('payment_details_update_detail_remove_api', kwargs={'pk': payment_details.id})
    client, _ = api_client_auth
    payload = {"card_number": "1234567891234567"}
    response = client.patch(url, payload, format='json')
    assert response.status_code == 200
    assert response.data["card_number"] == "1234567891234567"


@pytest.mark.django_db
def test_payment_details_detail(api_client_auth, payment_details):
    url = reverse('payment_details_update_detail_remove_api', kwargs={'pk': payment_details.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert "card_number" in response.data


@pytest.mark.django_db
def test_payment_details_delete(api_client_auth, payment_details):
    url = reverse('payment_details_update_detail_remove_api', kwargs={'pk': payment_details.id})
    client, _ = api_client_auth
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_shipping_address_list(api_client_auth, few_shipping_address):
    url = reverse('shipping_address_list_create_api')
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_shipping_address_create(api_client_auth, shipping_address, user2):
    url = reverse('shipping_address_list_create_api')
    client, _ = api_client_auth
    payload = {"street_address": '3th Avenue 456',
               "city": 'Oklahoma',
               "zip_code": '4567894356',
               "customer": user2.id}
    response = client.post(url, payload, format='json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_shipping_address_update(api_client_auth, shipping_address):
    url = reverse('shipping_address_update_detail_remove_api', kwargs={'pk': shipping_address.id})
    client, _ = api_client_auth
    payload = {"street_address": '3th Avenue 123'}
    response = client.patch(url, payload, format='json')
    assert response.status_code == 200
    assert response.data["street_address"] == "3th Avenue 123"


@pytest.mark.django_db
def test_shipping_address_detail(api_client_auth, shipping_address):
    url = reverse('shipping_address_update_detail_remove_api', kwargs={'pk': shipping_address.id})
    client, _ = api_client_auth
    response = client.get(url)
    assert response.status_code == 200
    assert "street_address" in response.data


@pytest.mark.django_db
def test_shipping_address_delete(api_client_auth, shipping_address):
    url = reverse('shipping_address_update_detail_remove_api', kwargs={'pk': shipping_address.id})
    client, _ = api_client_auth
    response = client.delete(url)
    assert response.status_code == 204
