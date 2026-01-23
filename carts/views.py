from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required

# Get or create cart
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart

# Add to cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, product=product, is_active=True)
        for item in cart_items:
            if set(item.variations.all()) == set(product_variation):
                if item.quantity < 10:
                    item.quantity += 1
                    item.save()
                return redirect('cart')

        cart_item = CartItem.objects.create(
            user=request.user,
            product=product,
            quantity=1,
        )
        cart_item.save()  # important to save before adding variations
        if product_variation:
            cart_item.variations.add(*product_variation)

    else:
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, product=product, is_active=True)
        for item in cart_items:
            if set(item.variations.all()) == set(product_variation):
                if item.quantity < 10:
                    item.quantity += 1
                    item.save()
                return redirect('cart')

        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1,
        )
        cart_item.save()  # important to save before adding variations
        if product_variation:
            cart_item.variations.add(*product_variation)

    return redirect('cart')

# Decrease quantity
def remove_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()  # Remove item if quantity reaches 0
    return redirect('cart')

# Remove entire item (regardless of quantity)
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

# Cart page
def cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    total = sum(item.product.price * item.quantity for item in cart_items)
    quantity = sum(item.quantity for item in cart_items)
    tax = (2 * total) / 100
    grand_total = total + tax

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)

# carts
def signin(request):
    return render(request, 'signin.html')  

@login_required(login_url='login')
def checkout(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        cart_items = []

    total = sum(item.product.price * item.quantity for item in cart_items)
    quantity = sum(item.quantity for item in cart_items)
    tax = (2 * total) / 100
    grand_total = total + tax

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/checkout.html', context)
