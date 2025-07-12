from django.contrib import admin
from .models import Item, SwapRequest, UserProfile, Cart, CartItem, Order, OrderItem, Notification

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'price', 'available', 'created_at']
    list_filter = ['available', 'category', 'created_at']
    search_fields = ['title', 'description']
    actions = ['approve_item', 'reject_item']

    def approve_item(self, request, queryset):
        queryset.update(available=True)

    def reject_item(self, request, queryset):
        queryset.update(available=False)

@admin.register(SwapRequest)
class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ['requester', 'item', 'status', 'created_at']
    list_filter = ['status', 'created_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'points']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    list_filter = ['created_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'item', 'quantity', 'added_at']
    list_filter = ['added_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username']
    readonly_fields = ['order_number']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'item', 'quantity', 'price', 'points']
    list_filter = ['order__status']