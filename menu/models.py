from django.db import models
from cloudinary.models import CloudinaryField 
# -------------------------------
# Category Model
# -------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# -------------------------------
# MenuItem Model
# -------------------------------
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.FloatField()
    image = CloudinaryField('image', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# -------------------------------
# Order Model
# -------------------------------
class Order(models.Model):
    PAYMENT_CHOICES = (
        ('cash', 'Cash'),
        ('online', 'Online'),
    )

    # Sequential primary key
    order_number = models.AutoField(primary_key=True)  # 1, 2, 3 ...

    # Small 4-digit serve code for menu/serve pages
    serve_code = models.CharField(max_length=4, unique=True, blank=True, null=True, editable=False)

    table_number = models.IntegerField(blank=True, null=True)
    total_amount = models.FloatField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Served, Delivered
    served = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        import random
        # Generate serve code only if not exists
        if not self.serve_code:
            while True:
                new_code = str(random.randint(1000, 9999))
                if not Order.objects.filter(serve_code=new_code).exists():
                    self.serve_code = new_code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} (Serve Code {self.serve_code})"


# -------------------------------
# OrderItem Model
# -------------------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} for Order {self.order.order_number}"
