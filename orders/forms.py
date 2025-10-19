from django import forms

class CheckoutForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        label='نام کامل',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-500 text-sm transition',
            'placeholder': 'نام و نام خانوادگی'
        })
    )
    
    phone = forms.CharField(
        max_length=11,
        label='شماره تماس',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-500 text-sm transition',
            'placeholder': '09xxxxxxxxx'
        })
    )
    
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-500 text-sm transition',
            'placeholder': 'example@email.com'
        })
    )
    
    postal_code = forms.CharField(
        max_length=10,
        label='کد پستی',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-500 text-sm transition',
            'placeholder': 'xxxxxxxxxx'
        })
    )
    
    address = forms.CharField(
        label='آدرس کامل',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-500 text-sm transition resize-none',
            'placeholder': 'آدرس کامل پستی شامل شهر، خیابان، کوچه، پلاک و ...',
            'rows': 4
        })
    )
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.startswith('09') or len(phone) != 11:
            raise forms.ValidationError("شماره تلفن باید با 09 شروع شود و 11 رقم باشد")
        return phone