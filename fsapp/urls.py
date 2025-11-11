from django.urls import path, include
from . import views

urlpatterns = [

    #1 json response
    #path('products/', views.products_list),
    
    #2 fbv
    path('products/', views.product_list),
    path('products/<int:pk>/', views.product_detail),
    path('orders/', views.order_list),

    #3 Aggregated Data
    path('products/info/', views.product_info),

    #4 CBV - Generics
    #4.1 Get All Products by Generic Class Based
    path('products/gen/', views.ProductsListAPIView.as_view()),
    path('orders/gen/', views.OrdersListAPIView.as_view()),
    #4.2 Get a specific Product
    path('products/gen/<int:pk>/', views.ProductDetailAPIView.as_view()),
    #path('products/gen/<int:product_id>/', views.ProductDetailAPIView.as_view()),



     
]