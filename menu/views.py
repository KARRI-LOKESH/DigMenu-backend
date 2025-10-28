from rest_framework import generics
from .models import Category, MenuItem, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, OrderSerializer
from django.http import HttpResponse
import qrcode
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay
import random
import requests
import os
import string 

# ------------------------------
# Categories List
# ------------------------------
class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# ------------------------------
# Menu Items List
# ------------------------------
class MenuItemList(generics.ListAPIView):
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        if category_id:
            return MenuItem.objects.filter(category_id=category_id)
        return MenuItem.objects.all()

# ------------------------------
# Order Create
# ------------------------------
class OrderCreate(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# ------------------------------
# Generate QR Code
# ------------------------------
def generate_qr(request):
    qr_folder = os.path.join("media", "qrcodes")
    os.makedirs(qr_folder, exist_ok=True)

    file_path = os.path.join(qr_folder, "menu_qr.png")
    url = "http://localhost:3000/menu/"
    img = qrcode.make(url)
    img.save(file_path)

    return HttpResponse("✅ QR code created at: " + file_path)

# ------------------------------
# Create Order After Payment
# ------------------------------
@csrf_exempt
@api_view(['POST'])
def create_order_after_payment(request):
    try:
        data = request.data
        items = data.get("items")
        total_amount = data.get("total_amount")
        table_number = data.get("table_number")

        if not items or not total_amount or not table_number:
            return Response({"error": "Missing required fields"}, status=400)

        # Create order
        order = Order.objects.create(
            table_number=table_number,
            total_amount=total_amount,
            payment_method="online",
            status="Paid"
        )

        # Create order items
        for i in items:
            menu_item_id = i.get("menu_item")
            qty = i.get("quantity")
            menu_item = MenuItem.objects.get(id=menu_item_id)
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=qty
            )

        return Response({
            "success": True,
            "order_number": order.order_number,
            "serve_code": order.serve_code
        })

    except Exception as e:
        print("Error:", e)
        return Response({"error": str(e)}, status=500)

# ------------------------------
# Razorpay Payment Verification
# ------------------------------
@csrf_exempt
@api_view(['POST'])
def verify_razorpay_payment(request):
    try:
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Verify signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })

        return Response({"success": True, "redirect_url": "/menu/"})

    except razorpay.errors.SignatureVerificationError:
        return Response({"error": "Payment verification failed"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# ------------------------------
# Admin Orders (all)
# ------------------------------
@api_view(["GET"])
def admin_orders(request):
    orders = Order.objects.all().order_by("-created_at")  # include served
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)
@csrf_exempt
@api_view(['POST'])
def update_order_status(request):
    order_number = request.data.get("order_number")
    serve_code = request.data.get("serve_code")
    status_value = request.data.get("status")

    if status_value not in ["Pending", "Confirmed", "Served", "Delivered"]:
        return Response({"error": "Invalid status"}, status=400)

    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    if status_value == "Delivered":
        if not serve_code:
            return Response({"error": "Serve code required for delivery"}, status=400)
        if str(order.serve_code).strip() != str(serve_code).strip():
            return Response({"error": "Incorrect serve code"}, status=400)
        order.status = "Delivered"
    else:
        order.status = status_value
        if status_value == "Served":
            order.served = True

    order.save()
    return Response({
        "success": True,
        "order_number": order.order_number,
        "status": order.status
    })
# ------------------------------
# Serve Order (mark as served)
# ------------------------------
@csrf_exempt
@api_view(["POST"])
def serve_order(request):
    order_number = request.data.get("order_number")

    try:
        order = Order.objects.get(order_number=order_number)
        if order.served:
            return Response({"message": "Order already served"}, status=200)

        order.served = True
        order.status = "Served"
        order.save()
        return Response({"message": "Order served successfully"}, status=200)

    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)


# ------------------------------
# CSRF Token (if needed)
# ------------------------------
@api_view(['GET'])
def get_csrf_token(request):
    token = get_token(request)
    return Response({"csrfToken": token})
