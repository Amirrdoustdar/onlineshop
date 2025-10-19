from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from cart.cart import Cart
from .models import Order
import requests
import json
from django.conf import settings
from decimal import Decimal

def order_confirm_view(request):
    cart = Cart(request)
    print("order_confirm_view called - Method:", request.method)

    if request.method == 'POST':
        # استفاده از request.POST مستقیم
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        shipping_method = request.POST.get('shipping_method', 'post')
        
        # 🔥 اصلاح هزینه‌های ارسال طبق اطلاعات جدید
        shipping_costs = {
            'tipax': Decimal('0'),        # پَس‌کرایه - رایگان برای خریدار
            'post': Decimal('80000'),     # پست پیشتاز
            'special_post': Decimal('140000'),  # پست ویژه
        }
        shipping_cost = shipping_costs.get(shipping_method, Decimal('80000'))
        
        # اعتبارسنجی ساده
        errors = []
        if not name:
            errors.append("نام کامل الزامی است")
        if not phone or len(phone) != 11:
            errors.append("شماره تلفن باید ۱۱ رقم باشد")
        if not email or '@' not in email:
            errors.append("ایمیل معتبر نیست")
        if not postal_code:
            errors.append("کد پستی الزامی است")
        if not address:
            errors.append("آدرس الزامی است")
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # محاسبه هزینه کل با احتساب ارسال
            total_with_shipping = cart.get_total_price() + shipping_cost
            
            # ذخیره اطلاعات در سشن
            order_data = {
                'full_name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'postal_code': postal_code,
                'shipping_method': shipping_method,
                'shipping_cost': str(shipping_cost),
                'total_price': str(total_with_shipping),
                'subtotal': str(cart.get_total_price()),  # مبلغ بدون هزینه ارسال
            }
            request.session['order_data'] = order_data
            print("Redirecting to payment_page...")
            return redirect('orders:payment_page')
    
    context = {
        'cart': cart,
    }
    return render(request, 'checkout_form.html', context)

def payment_page(request):
    """ایجاد درخواست پرداخت و انتقال به درگاه زرین پال"""
    if request.method != 'GET':
        messages.error(request, "دسترسی غیرمجاز")
        return redirect('orders:order_confirm_view')
    
    cart = Cart(request)
    
    # اطلاعات از سشن بگیر
    order_data = request.session.get('order_data')
    if not order_data:
        messages.error(request, "لطفا ابتدا اطلاعات سفارش را تکمیل کنید")
        return redirect('orders:order_confirm_view')
    
    # چک کن سبد خرید خالی نباشه
    if cart.get_total_price() == 0:
        messages.error(request, "سبد خرید شما خالی است")
        return redirect('cart:cart_detail')
    
    # تبدیل مبلغ
    amount = int(Decimal(order_data['total_price']))  # مبلغ به تومان
    description = f"پرداخت سفارش از نارنجی شاپ - مبلغ: {amount:,} تومان"

    # درخواست پرداخت به زرین پال
    data = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": amount * 10,  # تبدیل به ریال
        "description": description,
        "callback_url": request.build_absolute_uri('/orders/verify/'),  # ✅ استفاده از آدرس مطلق
        "metadata": {"mobile": order_data['phone'], "email": order_data['email']}  # ✅ متادیتا اضافه شده
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "https://api.zarinpal.com/pg/v4/payment/request.json",  # درخواست پرداخت
            data=json.dumps(data),
            headers=headers,
            timeout=10
        )
        
        result = response.json()
        print("نتیجه درخواست پرداخت زرین‌پال:", result)

        if result.get("data") and result["data"].get("code") == 100:
            # درخواست پرداخت موفق
            authority = result["data"]["authority"]
            
            # ذخیره authority در سشن
            request.session['payment_authority'] = authority
            
            # انتقال کاربر به درگاه پرداخت
            payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
            return redirect(payment_url)
            
        else:
            error_code = result.get("errors", {}).get("code", "نامشخص")
            error_message = result.get("errors", {}).get("message", "خطای نامشخص")
            
            messages.error(request, f"خطا در اتصال به درگاه پرداخت: {error_message}")
            return redirect('orders:payment_failed')
            
    except Exception as e:
        print("خطا در payment_page:", str(e))
        messages.error(request, "خطا در اتصال به درگاه پرداخت")
        return redirect('orders:payment_failed')

def verify_payment(request):
    """تأیید پرداخت زرین پال"""
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    
    if status == 'OK' and authority:
        try:
            # اطلاعات سفارش از سشن
            order_data = request.session.get('order_data', {})
            if not order_data:
                messages.error(request, "اطلاعات سفارش یافت نشد")
                return redirect('orders:order_confirm_view')
            
            amount = int(Decimal(order_data['total_price'])) * 10  # تبدیل به ریال
            
            # درخواست تأیید به زرین پال
            data = {
                "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                "amount": amount,
                "authority": authority
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                "https://api.zarinpal.com/pg/v4/payment/verify.json",
                data=json.dumps(data),
                headers=headers,
                timeout=10
            )
            
            result = response.json()
            print("نتیجه تأیید پرداخت زرین‌پال:", result)
            
            if result.get("data") and result["data"].get("code") == 100:
                # پرداخت موفق
                ref_id = result["data"]["ref_id"]
                
                # 🔥 ذخیره سفارش در دیتابیس با فیلدهای جدید
                order = Order.objects.create(
                    full_name=order_data['full_name'],
                    email=order_data['email'],
                    phone=order_data['phone'],
                    postal_code=order_data['postal_code'],
                    address=order_data['address'],
                    total_price=order_data['total_price'],
                    shipping_method=order_data['shipping_method'],  # 🔥 جدید
                    shipping_cost=order_data['shipping_cost'],      # 🔥 جدید
                    status='paid',
                    payment_authority=authority,
                    payment_reference=ref_id,
                )
                
                # پاک کردن سشن
                if 'order_data' in request.session:
                    del request.session['order_data']
                if 'payment_authority' in request.session:
                    del request.session['payment_authority']
                
                # خالی کردن سبد خرید
                cart = Cart(request)
                cart.clear()
                
                messages.success(request, f"پرداخت با موفقیت انجام شد. کد پیگیری: {ref_id}")
                return redirect('orders:payment_success')
            else:
                error_code = result.get("errors", {}).get("code", "نامشخص")
                error_message = result.get("errors", {}).get("message", "خطای نامشخص")
                
                # 🔥 ذخیره سفارش ناموفق با فیلدهای جدید
                Order.objects.create(
                    full_name=order_data['full_name'],
                    email=order_data['email'],
                    phone=order_data['phone'],
                    postal_code=order_data['postal_code'],
                    address=order_data['address'],
                    total_price=order_data['total_price'],
                    shipping_method=order_data['shipping_method'],  # 🔥 جدید
                    shipping_cost=order_data['shipping_cost'],      # 🔥 جدید
                    status='failed',
                    payment_authority=authority,
                )
                
                messages.error(request, f"پرداخت ناموفق: {error_message}")
                return redirect('orders:payment_failed')
                
        except Exception as e:
            print("خطا در verify_payment:", str(e))
            messages.error(request, "خطا در تأیید پرداخت")
            return redirect('orders:payment_failed')
    else:
        messages.error(request, "پرداخت لغو شد")
        return redirect('orders:payment_failed')

def payment_failed(request):
    """صفحه خطای پرداخت"""
    return render(request, 'orders/payment_failed.html')

def payment_success(request):
    """صفحه موفقیت پرداخت"""
    return render(request, 'orders/order_success.html')