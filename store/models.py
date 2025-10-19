from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='تصویر دسته‌بندی')
    
    # فیلدهای جدید برای نمایش در صفحه اصلی
    show_in_homepage = models.BooleanField(
        default=True,
        verbose_name='نمایش در صفحه اصلی',
        help_text='اگر تیک بخورد، این دسته‌بندی در صفحه اصلی نمایش داده می‌شود'
    )
    
    homepage_order = models.IntegerField(
        default=0,
        verbose_name='ترتیب نمایش در صفحه اصلی',
        help_text='عدد کمتر = نمایش زودتر'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])


# **مدل Color**
class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام رنگ')
    code = models.CharField(max_length=7, blank=True, null=True, verbose_name='کد رنگ (مثلاً #FF0000)')
    
    class Meta:
        verbose_name = 'رنگ'
        verbose_name_plural = 'رنگ‌ها'
    
    def __str__(self):
        return self.name


# **مدل Size**
class Size(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام سایز')
    
    class Meta:
        verbose_name = 'سایز'
        verbose_name_plural = 'سایزها'
    
    def __str__(self):
        return self.name

    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        validators=[MinValueValidator(Decimal('1'))]
    )
    old_price = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        blank=True,
        null=True,
        verbose_name='قیمت قبلی (برای نمایش تخفیف)'
    )
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True, default='products/placeholder-images-image_large.webp')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def has_variants(self):
        """بررسی اینکه آیا محصول variant دارد"""
        return self.variants.exists()
    
    def get_available_variants(self):
        """دریافت variantهای موجود"""
        return self.variants.filter(quantity__gt=0)
    
    def is_in_stock(self):
        """بررسی موجود بودن محصول"""
        if self.has_variants():
            return self.get_available_variants().exists()
        else:
            return self.stock > 0 and self.available
    
    def get_primary_image(self):
        """
        برگرداندن URL تصویر اصلی محصول
        اولویت: تصویر اصلی ProductImage > اولین ProductImage > فیلد image
        """
        try:
            # روش 1: تصویر اصلی از ProductImage
            primary_image = self.images.filter(is_primary=True).first()
            if primary_image and primary_image.image:
                return primary_image.image.url
        except Exception:
            pass
        
        try:
            # روش 2: اولین تصویر از ProductImage
            first_image = self.images.first()
            if first_image and first_image.image:
                return first_image.image.url
        except Exception:
            pass
        
        try:
            # روش 3: فیلد image مستقیم
            if self.image:
                return self.image.url
        except Exception:
            pass
        
        # اگر هیچ تصویری پیدا نشد
        return None
    
    def get_all_images(self):
        """دریافت همه تصاویر محصول به صورت لیست URL"""
        images_list = []
        
        # اضافه کردن تصویر اصلی ProductImage ابتدا
        try:
            primary = self.images.filter(is_primary=True).first()
            if primary and primary.image:
                images_list.append(primary.image.url)
        except Exception:
            pass
        
        # اضافه کردن بقیه تصاویر ProductImage
        try:
            for img in self.images.exclude(is_primary=True).order_by('order'):
                if img.image and img.image.url not in images_list:
                    images_list.append(img.image.url)
        except Exception:
            pass
        
        # اضافه کردن فیلد image اگر وجود داشت و قبلاً اضافه نشده
        try:
            if self.image and self.image.url not in images_list:
                images_list.append(self.image.url)
        except Exception:
            pass
        
        return images_list
    
    def get_discount_percent(self):
        """محاسبه درصد تخفیف"""
        if self.old_price and self.old_price > self.price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return int(discount)
        return 0
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name='محصول')
    image = models.ImageField(upload_to='products/%Y/%m/', verbose_name='تصویر')
    is_primary = models.BooleanField(default=False, verbose_name='تصویر اصلی')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصول'
    
    def __str__(self):
        return f"{self.product.name} - تصویر {self.order}"
    
    def save(self, *args, **kwargs):
        # اگر این تصویر به عنوان اصلی انتخاب شد، بقیه را غیر اصلی کن
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class GalleryImage(models.Model):
    """
    مدل برای نمایش تصاویر در گالری صفحه اصلی
    """
    title = models.CharField(
        max_length=200, 
        blank=True,
        null=True,
        verbose_name="عنوان تصویر (اختیاری)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات (اختیاری)"
    )
    image = models.ImageField(
        upload_to='gallery/', 
        verbose_name="تصویر"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="نمایش در سایت"
    )
    order = models.IntegerField(
        default=0, 
        verbose_name="ترتیب نمایش",
        help_text="عدد کمتر = نمایش زودتر"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "تصویر گالری"
        verbose_name_plural = "تصاویر گالری"
    
    def __str__(self):
        return self.title if self.title else f"تصویر گالری {self.id}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True, null=True, verbose_name='کد SKU')
    
    def is_available(self):
        """بررسی موجود بودن variant"""
        return self.quantity > 0
        
    class Meta:
        unique_together = ('product', 'color', 'size')
        verbose_name = 'نوع محصول'
        verbose_name_plural = 'انواع محصول'

    def __str__(self):
        parts = [self.product.name]
        if self.color:
            parts.append(str(self.color))
        if self.size:
            parts.append(str(self.size))
        return " - ".join(parts)
    

class Banner(models.Model):
    """
    بنرهای تبلیغاتی سایت (بین محصولات و درباره ما)
    """
    title = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="عنوان (اختیاری)"
    )
    image = models.ImageField(
        upload_to='banners/', 
        verbose_name="تصویر بنر"
    )
    link = models.URLField(
        blank=True, 
        null=True,
        verbose_name="لینک (اختیاری)",
        help_text="لینک به صفحه محصول یا دسته‌بندی"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="نمایش در سایت"
    )
    order = models.IntegerField(
        default=0, 
        verbose_name="ترتیب نمایش"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "بنر تبلیغاتی"
        verbose_name_plural = "بنرهای تبلیغاتی"
    
    def __str__(self):
        return self.title if self.title else f"بنر {self.id}"


class HomeSlider(models.Model):
    """
    اسلایدرهای صفحه اصلی بین محصولات و فوتر
    """
    SLIDER_TYPE_CHOICES = [
        ('slider1', 'اسلایدر اول'),
        ('slider2', 'اسلایدر دوم'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان اسلاید"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )
    image = models.ImageField(
        upload_to='home_sliders/',
        verbose_name="تصویر اسلاید"
    )
    link = models.URLField(
        blank=True,
        null=True,
        verbose_name="لینک (اختیاری)"
    )
    slider_type = models.CharField(
        max_length=10,
        choices=SLIDER_TYPE_CHOICES,
        default='slider1',
        verbose_name="نوع اسلایدر"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['slider_type', 'order', '-created_at']
        verbose_name = "اسلایدر صفحه اصلی"
        verbose_name_plural = "اسلایدرهای صفحه اصلی"
    
    def __str__(self):
        return f"{self.get_slider_type_display()} - {self.title}"