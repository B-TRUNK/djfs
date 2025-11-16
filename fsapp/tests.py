from django.test import TestCase
from fsapp.models import User, Order, Product
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Create your tests here.

# class UserOrderTestCase(TestCase):
#     def setUp(self):
#         user_1 = User.objects.create_user(username='usr1', password='test1')
#         user_2 = User.objects.create_user(username='usr2', password='test2')

#         Order.objects.create(user = user_1)
#         Order.objects.create(user = user_1)
#         Order.objects.create(user = user_2)
#         Order.objects.create(user = user_2)

#     def test_user_order_endpoint_retrieves_only_authenticated_user_orders(self):
#         user = User.objects.get(username='usr1')
#         self.client.force_login(user)
#         response = self.client.get(reverse('user_orders')) #name from Urls.py

#         assert response.status_code == status.HTTP_200_OK
#         #data = response.json()
#         orders = response.json()
#         self.assertTrue(all(order['user'] == user.id for order in orders))
#         #print(data)

#     def test_user_order_list_authenticated(self):
#         response = self.client.get(reverse('user_orders'))
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# # run test: manage.py test

class ProductsTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.normal_user = User.objects.create_user(username='user', password='userpass')
        self.product = Product.objects.create(
            name = 'Test Product',
            description = 'Test Description',
            price = 9.99,
            stock = 10
        )
        self.url = reverse('product-detail', kwargs={'product_id': self.product.pk})

    def test_get_product(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)


    # Make Sure no unauthorized user can update a product
    def test_unauthorized_update_product(self):
        data = {'name': 'Updated Product'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Make Sure no unauthorized user can delete a product
    def test_unauthorized_delete_product(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_admins_can_delete_products(self):
        
        # test normal user cannot delete
        self.client.login(username='user', password='userpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())


        # test Admin is able to delete
        self.client.login(username='admin', password='adminpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())


