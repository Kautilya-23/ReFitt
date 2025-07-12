from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    condition = models.CharField(max_length=50)
    tags = models.CharField(max_length=200)
    image = models.ImageField(upload_to='items/')
    points = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SwapRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_requests')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_placed', 'Order Placed'),
        ('swap_request', 'Swap Request'),
        ('order_status', 'Order Status Update'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    related_order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.recipient.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_total_price(self):
        total = Decimal('0.00')
        for cart_item in self.cartitem_set.all():
            total += cart_item.get_total_price
        return total
    
    @property
    def get_total_points(self):
        total = 0
        for cart_item in self.cartitem_set.all():
            total += cart_item.item.points * cart_item.quantity
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_total_price(self):
        return self.item.price * Decimal(str(self.quantity))

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_points = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    points = models.IntegerField(default=0)