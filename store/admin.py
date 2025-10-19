from django.contrib import admin
from django.utils.html import format_html
from django import forms
from decimal import Decimal
from .models import Category, Product, ProductImage, ProductVariant, Color, Size, GalleryImage, Banner, HomeSlider


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'image_preview', 'is_primary', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'پیش‌نمایش'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'price': forms.NumberInput(attrs={
                'step': '1',
                'min': '1',
                'placeholder': 'مثال: 155000 یا 450000'
            })
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price:
            if price % 1 != 0:
                raise forms.ValidationError("❌ قیمت باید عدد صحیح باشد.")
            if price < Decimal('1'):
                raise forms.ValidationError("❌ قیمت باید حداقل ۱ تومان باشد")
            if price > Decimal('1000000000'):
                raise forms.ValidationError("❌ قیمت نمی‌تواند بیشتر از ۱,۰۰۰,۰۰۰,۰۰۰ تومان باشد")
        return price


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'show_in_homepage', 'homepage_order', 'created_at']
    list_editable = ['show_in_homepage', 'homepage_order']
    list_filter = ['show_in_homepage', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('تنظیمات صفحه اصلی', {
            'fields': ('show_in_homepage', 'homepage_order'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['name', 'category', 'formatted_price', 'stock', 'available', 'main_image_preview']
    list_filter = ['available', 'category', 'created_at']
    list_editable = ['stock', 'available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    
    def formatted_price(self, obj):
        if obj.price:
            return f"{obj.price:,.0f} تومان"
        return "۰ تومان"
    formatted_price.short_description = 'قیمت'
    
    def main_image_preview(self, obj):
        url = obj.get_primary_image()
        if url:
            return format_html('<img src="{}" style="max-height: 40px;" />', url)
        return "-"
    main_image_preview.short_description = 'تصویر'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['product', 'is_primary']
    list_editable = ['is_primary', 'order']
    search_fields = ['product__name']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'پیش‌نمایش'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'size', 'quantity']
    list_filter = ['product', 'color', 'size']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']
    

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    
    
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'link', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active', 'order']
    fields = ['title', 'image', 'link', 'is_active', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "پیش‌نمایش"


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ['title', 'slider_type', 'order', 'is_active', 'image_preview']
    list_filter = ['slider_type', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "پیش‌نمایش"