from django.db import models
from store.models import Product 

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('failed', 'ناموفق'),
        ('canceled', 'لغو شده'),
    ]
    
    SHIPPING_METHODS = [
        ('tipax', 'تیپاکس (پس کرایه)'),
        ('post', 'پست پیشتاز'),
        ('special_post', 'پست ویژه'),
    ]
    
    full_name = models.CharField(max_length=100, verbose_name='نام کامل')
    email = models.EmailField(verbose_name='ایمیل')
    phone = models.CharField(max_length=15, verbose_name='شماره تماس')
    postal_code = models.CharField(max_length=10, verbose_name='کد پستی')
    address = models.TextField(verbose_name='آدرس')
    total_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='مبلغ کل')
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHODS, default='post', verbose_name='روش ارسال')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='هزینه ارسال')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    payment_authority = models.CharField(max_length=50, blank=True, verbose_name='کد مرجع پرداخت')
    payment_reference = models.CharField(max_length=50, blank=True, verbose_name='شماره پیگیری')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')  # 🔥 اضافه شد
    updated = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created']
    
    def __str__(self):
        return f"سفارش {self.id} - {self.full_name}"
    
    @property
    def paid(self):
        """ویژگی برای بررسی وضعیت پرداخت"""
        return self.status == 'paid'
    paid.fget.short_description = 'پرداخت شده'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='سفارش')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='قیمت')
    quantity = models.PositiveIntegerField(default=1, verbose_name='تعداد')
    
    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_cost(self):
        return self.price * self.quantity