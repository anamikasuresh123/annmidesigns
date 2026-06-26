from django.urls import path
from .views import (
    ApplyCouponView, HeritageView, HomeView, LoginView, ProductDetailView, RegisterView,
    LogoutView, CartView, AddToCartView,
    RemoveFromCartView, RentalView, SingleCheckoutView, WishlistView, AddToWishlistView,
    RemoveFromWishlistView, CheckoutView, OrdersView,
    ProfileView, KurtiView, anarkali, AllProductsView,SearchView,ChuridarView,BridalBlouseView,
      AdminDashboardView, AdminOrderStatusView,
    AdminDeleteProductView, AdminDeleteCouponView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:cart_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/<int:product_id>/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('collections/kurti/', KurtiView.as_view(), name='kurti'),
    path('collections/anarkali/', anarkali.as_view(), name='anarkali'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('all-products/', AllProductsView.as_view(), name='all_products'),
    path('search/', SearchView.as_view(), name='search'),
    path('collections/churidar/', ChuridarView.as_view(), name='churidar'),
    path('collections/bridal-blouse/', BridalBlouseView.as_view(), name='bridal_blouse'),
    path('heritage/', HeritageView.as_view(), name='heritage'),
    path('checkout/single/<int:cart_id>/', SingleCheckoutView.as_view(), name='single_checkout'),
    path('apply-coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/order/<int:order_id>/status/', AdminOrderStatusView.as_view(), name='admin_order_status'),
    path('admin-dashboard/product/<int:product_id>/delete/', AdminDeleteProductView.as_view(), name='admin_delete_product'),
    path('admin-dashboard/coupon/<int:coupon_id>/delete/', AdminDeleteCouponView.as_view(), name='admin_delete_coupon'),
    path('rental/', RentalView.as_view(), name='rental'),
        
]

