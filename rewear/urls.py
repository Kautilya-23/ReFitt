from django.urls import path
from . import views

app_name = 'rewear'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('browse/', views.browse_all_items, name='browse_all_items'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('add-item/', views.add_item, name='add_item'),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('swap-request/<int:item_id>/', views.swap_request, name='swap_request'),
    path('respond-swap-request/<int:swap_request_id>/<str:action>/', views.respond_to_swap_request, name='respond_to_swap_request'),
    path('redeem-points/<int:item_id>/', views.redeem_points, name='redeem_points'),
    path('notifications/', views.notifications, name='notifications'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
]