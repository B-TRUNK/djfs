from django.urls import path, include
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Simple-JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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
    path('products/gen/', views.ProductListCreateAPIView.as_view()),
    path('orders/gen/', views.OrdersListAPIView.as_view()),
    #4.2 Get a specific Product
    path('products/gen/<int:pk>/', views.ProductDetailAPIView.as_view()),
    #path('products/gen/<int:product_id>/', views.ProductDetailAPIView.as_view()),
    #4.3 Self Orders
    path('my-orders/', views.UserOrderListAPIView.as_view(), name='user_orders'),
    #5 - APIView
    path('products/apiv/', views.ProductInfoAPIView.as_view()),
    #6 Update/Delete APIView
    path('products/apiv/<int:pk>/', views.ProductUpdateDestroyAPIView.as_view()),


    #Adding Simple-JWT Routes
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #drf-Spectacular 
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]