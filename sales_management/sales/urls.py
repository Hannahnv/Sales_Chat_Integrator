from django.urls import path, include
from . import views
from .views import CustomerViewSet, ProductViewSet, OrderDetailViewSet, SearchViewSet, StatisticViewSets, ChatViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'home', StatisticViewSets, basename="home")
router.register(r'customers', CustomerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orderdetails', OrderDetailViewSet)
router.register(r'search', SearchViewSet, basename="search")
router.register(r'chat', ChatViewSet)

urlpatterns = [
    path('', views.index, name="index"),
    path('customers/', views.customer_list, name='customer_list'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customer/create/', views.customer_create, name='customer_create'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('orders/', views.order_list, name='order_list'),
    path('order/create/', views.order_create, name='order_create'),
    path('order/<str:order_code>/', views.order_detail, name='order_detail'),
    path('customer/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customer/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('order/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('order/<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('search/product_customers/<int:product_id>/', views.search_product_customers, name='search_product_customers'),
    path('search/customer_orders/<int:customer_id>/', views.search_customer_orders, name='search_customer_orders'),
    path('search/orders_by_product/', views.search_orders_by_product, name='search_orders_by_product'),
    path('search/orders_by_customer/', views.search_orders_by_customer, name='search_orders_by_customer'),
    path('upload/', views.upload_file, name='upload_file'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/login/', views.login_view, name='login'),
    path('api/', include(router.urls)), 
    path('chat/', views.chat_view, name='chat'),
    
]
