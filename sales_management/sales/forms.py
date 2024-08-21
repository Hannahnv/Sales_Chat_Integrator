from django import forms
from .models import Customer, Product, OrderDetail
from django.forms.widgets import DateTimeInput
import datetime

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_code', 'name', 'segment_code', 'segment_description']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_code', 'product_name', 'group_code', 'group_name', 'price']

class OrderDetailForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d %H:%M:%S'],
        initial=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    customer_name = forms.CharField(label='Customer Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = OrderDetail
        fields = ['order_code', 'customer', 'product', 'created_at', 'quantity', 'total_price']
        widgets = {
            'order_code': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    
    def save(self, commit=True):
        customer_name = self.cleaned_data['customer_name']
        customer, created = Customer.objects.get_or_create(name=customer_name)
        self.instance.customer = customer
        return super().save(commit=commit)

class UploadFileForm(forms.Form):
    file = forms.FileField()
    

