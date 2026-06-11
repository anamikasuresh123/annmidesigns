from django.contrib import admin
from .models import Category, Coupon, Product, Cart, Order

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display  = ('code', 'discount_percent', 'is_active', 'valid_to')
    filter_horizontal = ('products',)