from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Category, ProductVariant, Color, Size, GalleryImage, HomeSlider
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
import json

def home(request):
    """
    صفحه اصلی فروشگاه نارنجی - نسخه اصلاح شده
    """
    try:
        # گالری تصاویر
        try:
            gallery_images = GalleryImage.objects.all()[:5]
        except Exception as e:
            print(f"DEBUG: Error loading gallery images: {e}")
            gallery_images = []
        
        # دسته‌بندی‌ها
        try:
            categories = Category.objects.filter(
                show_in_homepage=True
            ).order_by('homepage_order', 'name')[:8]
        except Exception as e:
            print(f"DEBUG: Error loading categories: {e}")
            categories = []
        
        # محصولات ویژه - با دیباگ بیشتر
        try:
            featured_products = Product.objects.filter(
                available=True
            ).select_related('category').prefetch_related('images').order_by('-created_at')[:8]
            
            print(f"DEBUG: Found {featured_products.count()} featured products")
            
            for product in featured_products:
                print(f"DEBUG: Product: {product.name}, Available: {product.available}, Stock: {product.stock}")
            
        except Exception as e:
            print(f"DEBUG: Error loading featured products: {e}")
            featured_products = []
        
        # محصولات جدید
        try:
            new_products = Product.objects.filter(
                available=True
            ).select_related('category').prefetch_related('images').order_by('-created_at')[:8]
            
            print(f"DEBUG: Found {new_products.count()} new products")
            
        except Exception as e:
            print(f"DEBUG: Error loading new products: {e}")
            new_products = []
        
        # اسلایدر 1
        try:
            slider1_images = HomeSlider.objects.filter(
                slider_type='slider1', 
                is_active=True
            ).order_by('order')[:6]
        except Exception as e:
            print(f"DEBUG: Error loading slider1: {e}")
            slider1_images = []
        
        # اسلایدر 2
        try:
            slider2_images = HomeSlider.objects.filter(
                slider_type='slider2', 
                is_active=True
            ).order_by('order')[:6]
        except Exception as e:
            print(f"DEBUG: Error loading slider2: {e}")
            slider2_images = []
    
    except Exception as e:
        print(f"DEBUG: Major error in home view: {e}")
        categories = []
        gallery_images = []
        featured_products = []
        new_products = []
        slider1_images = []
        slider2_images = []
    
    # Context با نام‌های صحیح
    context = {
        'gallery_images': gallery_images,
        'categories': categories,
        'featured_products': featured_products,
        'new_products': new_products,
        'slider1_images': slider1_images,
        'slider2_images': slider2_images,
        'page_title': 'فروشگاه نارنجی',
        'is_home': True,
    }
    
    return render(request, 'store/product/list.html', context)

def product_list(request):
    """
    لیست محصولات - اضافه شده برای رفع خطا
    """
    try:
        # دریافت پارامترهای فیلتر
        category_slug = request.GET.get('category')
        search_query = request.GET.get('q', '').strip()
        
        # محصولات پایه
        products = Product.objects.filter(available=True)
        
        # فیلتر بر اساس دسته‌بندی
        current_category = None
        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)
        
        # فیلتر بر اساس جستجو
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        # مرتب‌سازی
        sort_by = request.GET.get('sort', '-created_at')
        if sort_by in ['price', '-price', 'name', '-name', '-created_at']:
            products = products.order_by(sort_by)
        else:
            products = products.order_by('-created_at')
        
        # دسته‌بندی‌ها برای فیلتر
        categories = Category.objects.all()
        
        # عنوان صفحه
        if current_category:
            page_title = f'{current_category.name} - نارنجی شاپ'
        elif search_query:
            page_title = f'جستجو برای: {search_query}'
        else:
            page_title = 'همه محصولات - نارنجی شاپ'
        
        context = {
            'products': products,
            'categories': categories,
            'current_category': current_category,
            'category_slug': category_slug,
            'query': search_query,
            'sort_by': sort_by,
            'products_count': products.count(),
            'page_title': page_title
        }
        
        return render(request, 'store/product/list.html', context)
        
    except Exception as e:
        print(f"DEBUG: Error in product_list: {e}")
        messages.error(request, "خطا در بارگذاری لیست محصولات")
        return redirect('store:home')

def product_list_by_category(request, category_slug):
    """
    لیست محصولات بر اساس دسته‌بندی - اضافه شده برای رفع خطا
    """
    try:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=category, 
            available=True
        ).order_by('-created_at')
        
        categories = Category.objects.all()
        
        context = {
            'products': products,
            'categories': categories,
            'current_category': category,
            'products_count': products.count(),
            'page_title': f'{category.name} - نارنجی شاپ'
        }
        
        return render(request, 'store/product/list.html', context)
        
    except Exception as e:
        print(f"DEBUG: Error in product_list_by_category: {e}")
        messages.error(request, "خطا در بارگذاری محصولات دسته‌بندی")
        return redirect('store:product_list')

def product_detail(request, slug):
    """
    جزئیات محصول - بهبود یافته
    """
    try:
        product = get_object_or_404(Product, slug=slug, available=True)
        
        # بررسی موجودی کلی محصول
        if not product.is_in_stock():
            messages.warning(request, "این محصول در حال حاضر ناموجود است.")
        
        # دریافت variants محصول
        variants = ProductVariant.objects.filter(product=product).select_related('color', 'size')
        
        # استخراج رنگ‌ها و سایزهای موجود
        available_colors = Color.objects.filter(
            productvariant__product=product,
            productvariant__quantity__gt=0
        ).distinct()
        
        available_sizes = Size.objects.filter(
            productvariant__product=product,
            productvariant__quantity__gt=0
        ).distinct()
        
        # اگر محصول variant ندارد، دکمه را فعال کن
        has_variants = variants.exists()
        
        # JSON برای جاوااسکریپت
        variants_data = []
        for variant in variants:
            variants_data.append({
                'id': variant.id,
                'color_id': variant.color.id if variant.color else None,
                'color_name': variant.color.name if variant.color else None,
                'size_id': variant.size.id if variant.size else None,
                'size_name': variant.size.name if variant.size else None,
                'quantity': variant.quantity,
                'available': variant.quantity > 0
            })
        
        variants_json = json.dumps(variants_data)
        
        # محصولات مرتبط - این خط اضافه شده
        related_products = Product.objects.filter(
            category=product.category, 
            available=True
        ).exclude(id=product.id)[:4]
        
        context = {
            'product': product,
            'variants': variants,
            'variants_json': variants_json,
            'colors': available_colors,
            'sizes': available_sizes,
            'has_variants': has_variants,
            'related_products': related_products,
            'category': product.category,
            'page_title': product.name
        }
        
        return render(request, 'store/product/detail.html', context)
        
    except Exception as e:
        print(f"DEBUG: Error in product_detail: {e}")
        messages.error(request, "خطا در بارگذاری اطلاعات محصول")
        return redirect('store:product_list')
def add_to_cart(request, product_id):
    """
    افزودن محصول به سبد خرید - نسخه ساده
    """
    try:
        from cart.cart import Cart
        
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id, available=True)
        
        # بررسی موجودی
        if not product.is_in_stock():
            messages.error(request, "این محصول در حال حاضر ناموجود است.")
            return redirect('store:product_detail', slug=product.slug)
        
        # افزودن به سبد خرید
        quantity = int(request.GET.get('quantity', 1))
        cart.add(product=product, quantity=quantity)
        
        messages.success(request, f"{quantity} عدد از '{product.name}' به سبد خرید اضافه شد.")
        return redirect('cart:cart_detail')
        
    except Exception as e:
        print(f"Error in add_to_cart: {e}")
        messages.error(request, "خطا در افزودن محصول به سبد خرید")
        return redirect('store:product_list')
        
def product_search(request):
    """
    جستجوی محصولات
    """
    query = request.GET.get('q', '').strip()
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(category__name__icontains=query),
            available=True
        ).distinct().order_by('-created_at')
    
    context = {
        'products': products,
        'query': query,
        'products_count': products.count() if products else 0,
        'categories': Category.objects.all(),
        'page_title': f'جستجو برای: {query}' if query else 'جستجو'
    }
    
    return render(request, 'store/product/search.html', context)

def faq(request):
    """
    صفحه سوالات متداول
    """
    context = {
        'page_title': 'سوالات متداول - نارنجی شاپ',
        'active_tab': 'faq'
    }
    return render(request, 'store/product/faq.html', context)

def shopping_guide(request):
    """
    صفحه راهنمای خرید
    """
    context = {
        'page_title': 'راهنمای خرید - نارنجی شاپ',
        'active_tab': 'shopping_guide'
    }
    return render(request, 'store/product/shopping_guide.html', context)

def contact(request):
    """
    صفحه تماس با ما
    """
    if request.method == 'POST':
        # پردازش فرم تماس
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # اعتبارسنجی ساده
        if not name or not email or not subject or not message:
            messages.error(request, "لطفاً تمام فیلدهای ضروری را پر کنید.")
        else:
            # در اینجا می‌توانید اطلاعات را در دیتابیس ذخیره کنید
            # یا ایمیل ارسال کنید
            messages.success(request, "پیام شما با موفقیت ارسال شد. به زودی با شما تماس خواهیم گرفت.")
            return redirect('store:contact')
    
    context = {
        'page_title': 'تماس با ما - نارنجی شاپ',
        'active_tab': 'contact'
    }
    return render(request, 'store/product/contact.html', context)

@csrf_exempt
def add_to_cart_ajax(request):
    """
    اضافه کردن محصول به سبد خرید با AJAX - بهبود یافته
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            color_id = data.get("color_id")
            size_id = data.get("size_id")
            quantity = int(data.get("quantity", 1))
            
            # اعتبارسنجی تعداد
            if quantity < 1 or quantity > 10:
                return JsonResponse({
                    "success": False, 
                    "error": "تعداد باید بین ۱ تا ۱۰ باشد."
                })
            
            # بررسی وجود محصول
            try:
                product = Product.objects.get(id=product_id, available=True)
            except Product.DoesNotExist:
                return JsonResponse({
                    "success": False, 
                    "error": "محصول موجود نیست یا غیرفعال است."
                })
            
            variant = None
            
            # اگر محصول variant دارد
            if product.has_variants():
                if not color_id or not size_id:
                    return JsonResponse({
                        "success": False, 
                        "error": "لطفاً رنگ و سایز را انتخاب کنید."
                    })
                
                # جستجوی variant مناسب
                try:
                    variant = ProductVariant.objects.get(
                        product=product,
                        color_id=color_id,
                        size_id=size_id
                    )
                    
                    if variant.quantity < quantity:
                        return JsonResponse({
                            "success": False, 
                            "error": f"تنها {variant.quantity} عدد از این محصول موجود است."
                        })
                        
                except ProductVariant.DoesNotExist:
                    return JsonResponse({
                        "success": False, 
                        "error": "این ترکیب رنگ و سایز موجود نیست."
                    })
            
            else:
                # محصول ساده بدون variant
                if product.stock < quantity:
                    return JsonResponse({
                        "success": False, 
                        "error": f"تنها {product.stock} عدد از این محصول موجود است."
                    })
            
            # در اینجا منطق اضافه کردن به سبد خرید را پیاده‌سازی کنید
            return JsonResponse({
                "success": True,
                "message": f"{quantity} عدد از {product.name} به سبد خرید اضافه شد.",
                "product_name": product.name,
                "quantity": quantity,
                "cart_count": 0
            })
            
        except Exception as e:
            print(f"Error in add_to_cart_ajax: {e}")
            return JsonResponse({
                "success": False, 
                "error": "خطای داخلی سرور. لطفاً دوباره تلاش کنید."
            })
    
    return JsonResponse({
        "success": False, 
        "error": "درخواست نامعتبر است."
    })

@csrf_exempt
def get_sizes_by_color(request):
    """
    دریافت سایزهای موجود برای رنگ انتخاب شده
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            color_id = data.get("color_id")
            
            sizes_query = ProductVariant.objects.filter(
                product_id=product_id,
                quantity__gt=0
            )
            
            if color_id:
                sizes_query = sizes_query.filter(color_id=color_id)
            
            sizes = sizes_query.values(
                'size__id', 'size__name', 'quantity'
            ).distinct()
            
            sizes_list = []
            for size in sizes:
                if size['size__id']:
                    sizes_list.append({
                        'id': size['size__id'],
                        'name': size['size__name'],
                        'quantity': size['quantity']
                    })
            
            return JsonResponse({
                "success": True,
                "sizes": sizes_list
            })
            
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": "خطا در دریافت سایزها"
            })
    
    return JsonResponse({"success": False, "error": "درخواست نامعتبر"})