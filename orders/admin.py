from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'full_name', 
        'email', 
        'phone', 
        'formatted_total_price', 
        'shipping_method', 
        'paid_display',  
        'status', 
        'created'
    ]
    
    list_filter = [
        'status', 
        'created', 
        'shipping_method'
    ]
    
    inlines = [OrderItemInline]
    search_fields = ['full_name', 'email', 'phone', 'postal_code']
    readonly_fields = ['created']
    
    def formatted_total_price(self, obj):
        return f"{obj.total_price:,.0f} تومان" if obj.total_price else "۰ تومان"
    formatted_total_price.short_description = 'مبلغ کل'
    
    def paid_display(self, obj):
        return obj.status == 'paid'
    paid_display.short_description = 'پرداخت شده'
    paid_display.boolean = True

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'order', 
        'product', 
        'formatted_price', 
        'quantity'
    ]
    
    list_filter = [
        'order__status', 
        'order__created'
    ]
    
    def formatted_price(self, obj):
        return f"{obj.price:,.0f} تومان" if obj.price else "۰ تومان"
    formatted_price.short_description = 'قیمت'