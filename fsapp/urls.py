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
]