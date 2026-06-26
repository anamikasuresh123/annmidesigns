from django.utils import timezone  # ✅ ഇത് മാത്രം മതി
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Coupon, Product, Cart, Order, Wishlist, Profile, Review


class HomeView(View):
    def get(self, request):
        products = Product.objects.all()[:4]
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        coupons = Coupon.objects.filter(is_active=True, valid_to__gte=timezone.now())
        return render(request, 'store/home.html', {
            'products': products,
            'cart_count': cart_count,
            'coupons': coupons,
        })


class LoginView(View):
    def get(self, request):
        return render(request, 'store/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'store/login.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'store/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            return redirect('login')
        return render(request, 'store/register.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')


class CartView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})


class AddToCartView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return redirect('cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, cart_id):
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        cart_item.delete()
        return redirect('cart')


class WishlistView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        wishlist_items = Wishlist.objects.filter(user=request.user)
        return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})


class AddToWishlistView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.get_or_create(user=request.user, product=product)
        return redirect('wishlist')


class RemoveFromWishlistView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, wishlist_id):
        item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        item.delete()
        return redirect('wishlist')


import urllib.parse

class CheckoutView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        full_name = request.POST['full_name']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        pincode = request.POST['pincode']
        
        items_text = ""
        total = 0
        for item in cart_items:
            items_text += f"- {item.product.name} x{item.quantity} = ₹{item.product.price * item.quantity}\n"
            total += item.product.price * item.quantity
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                full_name=full_name,
                phone=phone,
                address=address,
                city=city,
                pincode=pincode
            )
        cart_items.delete()
        
        message = f"""🛍️ *New Order - AnmiDesigns!*

👤 *Customer:* {full_name}
📞 *Phone:* {phone}
📧 *Email:* {request.user.email}

📦 *Items:*
{items_text}
💰 *Total:* ₹{total}

📍 *Delivery Address:*
{address}
{city} - {pincode}"""

        whatsapp_url = f"https://wa.me/918606826558?text={urllib.parse.quote(message)}"
        return redirect(whatsapp_url)


class SingleCheckoutView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, cart_id):
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        return render(request, 'store/checkout.html', {
            'cart_items': [cart_item],
            'total': cart_item.product.price * cart_item.quantity,
            'single_id': cart_id,
        })

    def post(self, request, cart_id):
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        full_name = request.POST['full_name']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        pincode = request.POST['pincode']
        
        Order.objects.create(
            user=request.user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode
        )
        cart_item.delete()
        
        message = f"""🛍️ *New Order - AnmiDesigns!*

👤 *Customer:* {full_name}
📞 *Phone:* {phone}
📧 *Email:* {request.user.email}

📦 *Item:* {cart_item.product.name} x{cart_item.quantity}
💰 *Total:* ₹{cart_item.product.price * cart_item.quantity}

📍 *Delivery Address:*
{address}
{city} - {pincode}"""

        whatsapp_url = f"https://wa.me/918606826558?text={urllib.parse.quote(message)}"
        return redirect(whatsapp_url)

class OrdersView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
        return render(request, 'store/orders.html', {'orders': orders})


class ProfileView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        order_count = Order.objects.filter(user=request.user).count()
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/profile.html', {
            'order_count': order_count,
            'wishlist_count': wishlist_count,
            'cart_count': cart_count,
        })

    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
        return redirect('profile')
        


class KurtiView(View):
    def get(self, request):
        products = Product.objects.filter(category__name__icontains='kurti')
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/kurti.html', {'products': products, 'cart_count': cart_count})


class anarkali(View):
    def get(self, request):
        products = Product.objects.filter(category__name__icontains='anarkali')
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/anarkali.html', {'products': products, 'cart_count': cart_count})


class ChuridarView(View):
    def get(self, request):
        products = Product.objects.filter(category__name__icontains='churithar')
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/churidar.html', {'products': products, 'cart_count': cart_count})


class BridalBlouseView(View):
    def get(self, request):
        products = Product.objects.filter(category__name__icontains='blouse design')
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/bridal_blouse.html', {'products': products, 'cart_count': cart_count})


class AllProductsView(View):
    def get(self, request):
        products = Product.objects.all()
        coupons = Coupon.objects.filter(is_active=True, valid_to__gt=timezone.now())
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/all_products.html', {'products': products, 'coupons': coupons, 'cart_count': cart_count})


class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        products = Product.objects.filter(name__icontains=query) if query else Product.objects.none()
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/search.html', {'products': products, 'query': query, 'cart_count': cart_count})


class HeritageView(View):
    def get(self, request):
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/heritage.html', {'cart_count': cart_count})


class ProductDetailView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        reviews = Review.objects.filter(product=product).order_by('-created_at')
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/product_detail.html', {
            'product': product,
            'cart_count': cart_count,
            'reviews': reviews,
        })

    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return redirect('login')
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment
            )
        return redirect('product_detail', product_id=product_id)


from django.http import JsonResponse
from .models import Product, Cart, Order, Wishlist, Profile, Review, Coupon
from django.utils import timezone
from django.utils import timezone

class ApplyCouponView(View):
    def get(self, request):
        code = request.GET.get('code', '').strip().upper()
        total = float(request.GET.get('total', 0))
        product_id = request.GET.get('product_id', None)
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True, valid_to__gte=timezone.now())
            # Check if coupon is for specific products
            if coupon.products.exists() and product_id:
                if not coupon.products.filter(id=product_id).exists():
                    return JsonResponse({
                        'valid': False,
                        'message': 'This coupon is not valid for this product!'
                    })
            discount = coupon.discount_percent
            new_total = round(total - (total * discount / 100), 2)
            return JsonResponse({
                'valid': True,
                'discount': discount,
                'new_total': new_total,
            })
        except Coupon.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'message': 'Invalid or expired coupon code!'
            })

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator

def admin_required(view_func):
    decorated = user_passes_test(lambda u: u.is_staff, login_url='/login/')(view_func)
    return decorated

@method_decorator(admin_required, name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        from django.contrib.auth.models import User
        total_orders = Order.objects.count()
        total_products = Product.objects.count()
        total_users = User.objects.count()
        total_revenue = sum([o.product.price * o.quantity for o in Order.objects.all()])
        orders = Order.objects.all().order_by('-ordered_at')[:50]
        products = Product.objects.all()
        users = User.objects.all().order_by('-date_joined')
        coupons = Coupon.objects.all()
        return render(request, 'store/admin_dashboard.html', {
            'total_orders': total_orders,
            'total_products': total_products,
            'total_users': total_users,
            'total_revenue': total_revenue,
            'orders': orders,
            'products': products,
            'users': users,
            'coupons': coupons,
        })

@method_decorator(admin_required, name='dispatch')
class AdminOrderStatusView(View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.status = request.POST.get('status', 'Pending')
        order.save()
        return redirect('/admin-dashboard/')

@method_decorator(admin_required, name='dispatch')
class AdminDeleteProductView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return redirect('/admin-dashboard/')

@method_decorator(admin_required, name='dispatch')
class AdminDeleteCouponView(View):
    def get(self, request, coupon_id):
        coupon = get_object_or_404(Coupon, id=coupon_id)
        coupon.delete()
        return redirect('/admin-dashboard/')            
    

class RentalView(View):
    def get(self, request):
        products = Product.objects.filter(category__name__icontains='Rental')
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        return render(request, 'store/rental.html', {'products': products, 'cart_count': cart_count})    