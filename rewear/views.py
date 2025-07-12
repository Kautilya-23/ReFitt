from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Item, SwapRequest, UserProfile, Cart, CartItem, Order, OrderItem, Notification
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth import authenticate
import uuid

def landing(request):
    items = Item.objects.filter(available=True)[:6]
    return render(request, 'landing.html', {'featured_items': items})

def browse_all_items(request):
    items = Item.objects.filter(available=True).order_by('-created_at')
    return render(request, 'browse_items.html', {'items': items})

@login_required
def dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    items = Item.objects.filter(user=request.user)
    swap_requests = SwapRequest.objects.filter(requester=request.user)
    incoming_swap_requests = SwapRequest.objects.filter(item__user=request.user, status='pending')
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)[:5]
    return render(request, 'dashboard.html', {
        'user_profile': user_profile, 
        'items': items, 
        'swap_requests': swap_requests,
        'incoming_swap_requests': incoming_swap_requests,
        'notifications': notifications
    })

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'item_detail.html', {'item': item})

@login_required
def add_item(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        category = request.POST['category']
        type = request.POST['type']
        size = request.POST['size']
        condition = request.POST['condition']
        tags = request.POST['tags']
        price = request.POST.get('price', 0)
        image = request.FILES.get('image')
        
        Item.objects.create(
            user=request.user,
            title=title,
            description=description,
            category=category,
            type=type,
            size=size,
            condition=condition,
            tags=tags,
            price=price,
            image=image
        )
        messages.success(request, 'Item added successfully!')
        return redirect('rewear:dashboard')
    return render(request, 'add_item.html')

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if user is trying to add their own item
    if item.user == request.user:
        messages.error(request, 'You cannot add your own items to cart.')
        return redirect('rewear:item_detail', item_id=item.id)
    
    if item.available:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        messages.success(request, f'{item.title} added to cart!')
    else:
        messages.error(request, 'This item is not available.')
    
    return redirect('rewear:item_detail', item_id=item.id)

@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('rewear:view_cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items})

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        if shipping_address and cart_items.exists():
            # Generate unique order number
            order_number = f"REF-{uuid.uuid4().hex[:8].upper()}"
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                total_amount=cart.get_total_price(),
                total_points=cart.get_total_points(),
                shipping_address=shipping_address
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    price=cart_item.item.price,
                    points=cart_item.item.points
                )
                # Mark item as unavailable
                cart_item.item.available = False
                cart_item.item.save()
                
                # Create notification for item owner
                Notification.objects.create(
                    recipient=cart_item.item.user,
                    notification_type='order_placed',
                    title=f'Your item "{cart_item.item.title}" has been ordered!',
                    message=f'{request.user.username} has placed an order for your item "{cart_item.item.title}" for ₹{cart_item.item.price}. Order number: {order_number}',
                    related_item=cart_item.item,
                    related_order=order
                )
            
            # Clear cart
            cart.delete()
            
            messages.success(request, f'Order placed successfully! Order number: {order_number}')
            return redirect('rewear:order_confirmation', order_id=order.id)
        else:
            messages.error(request, 'Please provide shipping address and ensure cart is not empty.')
    
    return render(request, 'checkout.html', {'cart': cart, 'cart_items': cart_items})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

@login_required
def swap_request(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        swap_request = SwapRequest.objects.create(requester=request.user, item=item, status='pending')
        
        # Create notification for item owner
        Notification.objects.create(
            recipient=item.user,
            notification_type='swap_request',
            title=f'New swap request for "{item.title}"',
            message=f'{request.user.username} has requested to swap your item "{item.title}". Check your dashboard to accept or reject the request.',
            related_item=item
        )
        
        messages.success(request, 'Swap request sent!')
        return redirect('rewear:item_detail', item_id=item.id)
    return render(request, 'item_detail.html', {'item': item})

@login_required
def redeem_points(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST' and user_profile.points >= item.points:
        user_profile.points -= item.points
        user_profile.save()
        item.available = False
        item.save()
        messages.success(request, 'Item redeemed!')
        return redirect('rewear:dashboard')
    return render(request, 'item_detail.html', {'item': item})

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, user=request.user)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted successfully!')
        return redirect('rewear:dashboard')
    return render(request, 'delete_item_confirm.html', {'item': item})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('rewear:dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('rewear:landing')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('rewear:notifications')

@login_required
def respond_to_swap_request(request, swap_request_id, action):
    swap_request = get_object_or_404(SwapRequest, id=swap_request_id, item__user=request.user)
    
    if action == 'accept':
        swap_request.status = 'accepted'
        swap_request.item.available = False
        swap_request.item.save()
        
        # Create notification for requester
        Notification.objects.create(
            recipient=swap_request.requester,
            notification_type='swap_request',
            title=f'Swap request accepted for "{swap_request.item.title}"',
            message=f'Your swap request for "{swap_request.item.title}" has been accepted by {request.user.username}.',
            related_item=swap_request.item
        )
        
        messages.success(request, 'Swap request accepted!')
    elif action == 'reject':
        swap_request.status = 'rejected'
        
        # Create notification for requester
        Notification.objects.create(
            recipient=swap_request.requester,
            notification_type='swap_request',
            title=f'Swap request rejected for "{swap_request.item.title}"',
            message=f'Your swap request for "{swap_request.item.title}" has been rejected by {request.user.username}.',
            related_item=swap_request.item
        )
        
        messages.success(request, 'Swap request rejected!')
    
    swap_request.save()
    return redirect('rewear:dashboard')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                UserProfile.objects.create(user=user)
                login(request, user)
                return redirect('rewear:dashboard')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'signup.html')