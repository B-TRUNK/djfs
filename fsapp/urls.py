from django.urls import path, include
from . import views

urlpatterns = [
    #1 json response
    path('products/', views.products_list),
    #1 fbv
    path('products/', views.products_list),
    path('products/<int:pk>/', views.product_details),

]