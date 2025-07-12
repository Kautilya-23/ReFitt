from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rewear.models import Item, Cart, CartItem, Order, OrderItem, SwapRequest, UserProfile

class Command(BaseCommand):
    help = 'Clear all user accounts and related data from the database'

    def handle(self, *args, **options):
        self.stdout.write("Clearing all user accounts and related data...")
        
        # Delete all related data first (due to foreign key constraints)
        OrderItem.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Order items deleted"))
        
        Order.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Orders deleted"))
        
        CartItem.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Cart items deleted"))
        
        Cart.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Carts deleted"))
        
        SwapRequest.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Swap requests deleted"))
        
        Item.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Items deleted"))
        
        UserProfile.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ User profiles deleted"))
        
        # Delete all users last
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ User accounts deleted"))
        
        self.stdout.write(self.style.SUCCESS("\n🎉 All data cleared successfully!"))
        self.stdout.write("The database is now empty and ready for fresh data.") 