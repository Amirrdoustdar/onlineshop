
from decimal import Decimal
from django.conf import settings
from store.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.clean_invalid_items()  # تمیز کردن آیتم‌های نامعتبر هنگام ایجاد

    def clean_invalid_items(self):
        """حذف آیتم‌های نامعتبر از سبد خرید"""
        invalid_items = []
        for product_id in self.cart.keys():
            try:
                # بررسی معتبر بودن ID
                int(product_id)
            except (ValueError, TypeError):
                invalid_items.append(product_id)
                continue
        
        # حذف آیتم‌های نامعتبر
        for item_id in invalid_items:
            if item_id in self.cart:
                del self.cart[item_id]
        
        if invalid_items:
            self.save()

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        
        # بررسی موجودی محصول
        if quantity > product.stock:
            raise ValueError(f"موجودی کافی نیست. فقط {product.stock} عدد موجود است.")
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0, 
                'price': str(product.price),
                'name': product.name  # ذخیره نام برای مواردی که محصول حذف شده
            }
        
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = list(self.cart.keys())
        
        # دریافت محصولات معتبر از دیتابیس
        valid_product_ids = []
        for pid in product_ids:
            try:
                pid_int = int(pid)
                valid_product_ids.append(pid_int)
            except (ValueError, TypeError):
                continue
        
        products = Product.objects.filter(id__in=valid_product_ids)
        product_dict = {str(product.id): product for product in products}
        
        # ساخت کپی از سبد خرید برای تکرار
        cart_copy = self.cart.copy()
        
        for product_id, item_data in cart_copy.items():
            if product_id in product_dict:
                product = product_dict[product_id]
                yield {
                    'product': product,
                    'quantity': item_data['quantity'],
                    'price': Decimal(item_data['price']),
                    'total_price': Decimal(item_data['price']) * item_data['quantity']
                }

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        total = Decimal(0)
        for item in self.cart.values():
            try:
                total += Decimal(item['price']) * item['quantity']
            except (ValueError, TypeError):
                continue
        return total

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()

    def get_item_count(self):
        """تعداد کل آیتم‌ها در سبد خرید"""
        return len(self.cart)