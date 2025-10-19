from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/category/<slug:category_slug>/', views.product_list_by_category, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('search/', views.product_search, name='product_search'),
    path('faq/', views.faq, name='faq'),
    path('shopping-guide/', views.shopping_guide, name='shopping_guide'),
    path('contact/', views.contact, name='contact'),
    
    # API endpoints
    path('api/add-to-cart/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('api/get-sizes/', views.get_sizes_by_color, name='get_sizes_by_color'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)