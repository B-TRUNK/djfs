from django.test import TestCase
from fsapp.models import User, Order
from django.urls import reverse
from rest_framework import status

# Create your tests here.

class UserOrderTestCase(TestCase):
    def setUp(self):
        user_1 = User.objects.create_user(username='usr1', password='test1')
        user_2 = User.objects.create_user(username='usr2', password='test2')

        Order.objects.create(user = user_1)
        Order.objects.create(user = user_1)
        Order.objects.create(user = user_2)
        Order.objects.create(user = user_2)

    def test_user_order_endpoint_retrieves_only_authenticated_user_orders(self):
        user = User.objects.get(username='usr1')
        self.client.force_login(user)
        response = self.client.get(reverse('user_orders')) #name from Urls.py

        assert response.status_code == status.HTTP_200_OK
        #data = response.json()
        orders = response.json()
        self.assertTrue(all(order['user'] == user.id for order in orders))
        #print(data)

    def test_user_order_list_authenticated(self):
        response = self.client.get(reverse('user_orders'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# run test: manage.py test