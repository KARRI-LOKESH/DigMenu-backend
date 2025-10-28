from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem, Order, OrderItem
from django.shortcuts import render, redirect
from django import forms
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'image_tag')
    list_filter = ('category',)
    search_fields = ('name',)
    list_editable = ('price',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:60px;height:60px;object-fit:cover;border-radius:5px;" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

from django.contrib import admin
from .models import Order, OrderItem

# Inline display of OrderItems in Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'quantity')
    can_delete = False
class DeliverForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    serve_code = forms.CharField(max_length=4, required=True)
# Custom admin for Orders
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'serve_code', 'table_number', 'total_amount', 'payment_method', 'status', 'served', 'created_at')
    list_filter = ('status', 'served', 'payment_method', 'created_at')
    search_fields = ('order_number', 'serve_code', 'table_number')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    actions = ['deliver_with_code']

    def deliver_with_code(self, request, queryset):
        if 'apply' in request.POST:
            serve_code = request.POST['serve_code']
            updated = 0
            for order in queryset:
                if str(order.serve_code) == serve_code:
                    order.status = "Delivered"
                    order.save()
                    updated += 1
            self.message_user(request, f"{updated} order(s) delivered successfully with serve code {serve_code}")
            return redirect(request.get_full_path())
        return render(request, 'admin/deliver_order.html', {'orders': queryset})
    deliver_with_code.short_description = "Deliver selected orders with serve code"

# Optional: Admin for OrderItem (if you want to manage separately)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity')
    list_filter = ('menu_item',)
    search_fields = ('order__order_number', 'menu_item__name')
