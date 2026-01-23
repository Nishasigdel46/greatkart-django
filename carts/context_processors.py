from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0

    try:
        if request.user.is_authenticated:
            # Get all CartItems for this user
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            # Get cart for session safely
            cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
            if cart:
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            else:
                cart_items = []

        # Count total quantity
        for item in cart_items:
            cart_count += item.quantity

    except:
        cart_count = 0

    return {'cart_count': cart_count}
