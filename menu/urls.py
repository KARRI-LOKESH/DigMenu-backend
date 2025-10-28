from django.urls import path
from .views import (
    CategoryList,
    MenuItemList,
    OrderCreate,
    create_order_after_payment,
    admin_orders,
    update_order_status,
    get_csrf_token,
    generate_qr,
    verify_razorpay_payment,
    serve_order,
)

urlpatterns = [
    path('categories/', CategoryList.as_view(), name='categories'),
    path('menu-items/', MenuItemList.as_view(), name='menu_items'),
    path('order/', OrderCreate.as_view(), name='order'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('generate-qr/', generate_qr, name='generate_qr'),
    path('create-order-after-payment/', create_order_after_payment, name='create_order_after_payment'),
    path('verify-razorpay-payment/', verify_razorpay_payment, name='verify_razorpay_payment'),
    path('admin/orders/', admin_orders, name='admin_orders'),
    path('serve-order/', serve_order, name='serve_order'),
    path('update-order-status/', update_order_status, name='update_order_status'),
]
