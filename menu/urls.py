from django.urls import path
from .views import CategoryList, MenuItemList, OrderCreate, create_order_after_payment, admin_orders, update_order_status, get_csrf_token   
from . import views
urlpatterns = [
    path('categories/', CategoryList.as_view()),
    path('menu-items/', MenuItemList.as_view()),
    path('order/', OrderCreate.as_view()),
    path("get-csrf-token/", get_csrf_token),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
    path('create-order-after-payment/', create_order_after_payment, name='create_order_after_payment'),
    path('verify-razorpay-payment/', views.verify_razorpay_payment, name='verify_razorpay_payment'),
    path('admin/orders/', admin_orders, name='admin_orders'),
    path('serve-order/', views.serve_order, name='serve_order'),
    path('update-order-status/', update_order_status, name='update_order_status'),

]
