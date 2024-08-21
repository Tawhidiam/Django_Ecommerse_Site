from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views import generic
from .carts import Cart
from .models import Coupon
from product.models import Product
# Create your views here.

class AddToCart(generic.View):
    def post(self, *args, **kwargs):
        product = get_object_or_404(Product, id = kwargs.get('product_id'))
        cart = Cart(self.request)
        cart.update(product.id, 1)
        return redirect('cart')


class CartItems(generic.TemplateView):
    template_name = "cart/cart.html"
    def get(self, request, *args, **kwargs):
        product_id = request.GET.get('product_id', None)
        quantity = request.GET.get('quantity', None)
        clear = request.GET.get('clear', False)
        cart = Cart(request)

        if product_id and quantity:
            product = get_object_or_404(Product, id=product_id)
            if product.in_stock:
                cart.update(int(product_id), int(quantity))
                return redirect('cart')
            else:
                messages.warning(request, 'The product is not in stock anymore!')
                return redirect('cart')

        if clear:
            cart.clear()
            return redirect('cart')
        
        return super().get(request, *args, **kwargs)

class AddCoupon(generic.View):
    def post(self, *args, **kwargs):
        code = self.request.POST.get('coupon', '')
        coupon = Coupon.objects.filter(code__iexact=code)
        cart = Cart(self.request)

        if coupon.exists():
            coupon = coupon.first()
            current_date = datetime(timezone.now())
            active_date = coupon.active_date
            expiry_date = coupon.expiry_date
            if current_date > expiry_date:
                messages.warning(self.request, "This Coupon Is Expired")
                return redirect('cart')
            if current_date < active_date:
                messages.warning(self.request, 'This coupon is not activated yet!')
                return redirect('cart')
            cart.add_coupon(coupon.id)
            messages.warning(self.request, 'Coupon added successfully!')
            return redirect('cart')
        else:
            messages.warning(self.request, "Invalid Coupon Code")
            return redirect('cart')