
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from store.models import Product
from .cart import Cart

def cart_add(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        
        # گرفتن تعداد از پارامترهای درخواست
        quantity = int(request.GET.get('quantity', 1))
        
        # بررسی محدودیت تعداد
        if quantity < 1 or quantity > 10:
            messages.error(request, "تعداد باید بین ۱ تا ۱۰ باشد.")
            return redirect('store:product_detail', slug=product.slug)
        
        # بررسی موجودی
        if product.stock < quantity:
            messages.warning(
                request, 
                f"موجودی کافی برای '{product.name}' وجود ندارد. فقط {product.stock} عدد موجود است."
            )
            return redirect('store:product_detail', slug=product.slug)
        
        # افزودن به سبد خرید
        cart.add(product=product, quantity=quantity)
        
        messages.success(
            request, 
            f"{quantity} عدد از '{product.name}' با موفقیت به سبد خرید اضافه شد."
        )
        
    except ValueError as e:
        messages.error(request, f"خطا در افزودن به سبد خرید: {str(e)}")
    except Exception as e:
        messages.error(request, "خطای غیرمنتظره‌ای رخ داد.")
    
    return redirect('cart:cart_detail')

def cart_remove(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        messages.success(request, f"'{product.name}' از سبد خرید حذف شد.")
    except Exception as e:
        messages.error(request, "خطا در حذف محصول از سبد خرید.")
    
    return redirect('cart:cart_detail')

def remove_invalid_item(request):
    """
    حذف آیتم‌های نامعتبر از سبد خرید
    """
    if request.method == "POST":
        cart = Cart(request)
        # اینجا منطق حذف آیتم‌های نامعتبر را اضافه کن
        # برای مثال:
        cart.clean_invalid_items()
        messages.success(request, "آیتم‌های نامعتبر حذف شدند.")
    
    return redirect('cart:cart_detail')
    
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})