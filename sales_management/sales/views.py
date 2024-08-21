from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Product, OrderDetail
from .forms import CustomerForm, ProductForm, OrderDetailForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth.decorators import user_passes_test

def staff_check(user):
    return user.is_staff

@login_required
def index(request):
    customer_count = Customer.objects.count()
    product_count = Product.objects.count()
    order_count = OrderDetail.objects.count()
    context = {
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
    }
    return render(request, 'index.html', context)

@login_required
@user_passes_test(staff_check)
def customer_list(request):
    customers = Customer.objects.all().order_by('customer_code')
    paginator = Paginator(customers, 1000)  
    page = request.GET.get('page')
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
    return render(request, 'sales/customer_list.html', {'customers': customers})


@login_required
@user_passes_test(staff_check)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'sales/customer_detail.html', {'customer': customer})

@login_required
@user_passes_test(staff_check)

def customer_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = CustomerForm(data)
        if form.is_valid():
            customer = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Customer created successfully',
                'customer_id': customer.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Form validation failed',
                'errors': form.errors
            })
    else:
        form = CustomerForm()
    return render(request, 'sales/customer_form.html', {'form': form})

@user_passes_test(staff_check)
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'sales/customer_form.html', {'form': form, 'edit': True, 'customer': customer})

@user_passes_test(staff_check)
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'sales/customer_delete.html', {'customer': customer})

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'sales/product_list.html', {'products': products})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sales/product_detail.html', {'product': product})

@login_required
@user_passes_test(staff_check)
def product_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = ProductForm(data)
        if form.is_valid():
            product = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Product created successfully',
                'product_id': product.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Form validation failed',
                'errors': form.errors
            })
    else:
        form = ProductForm()
    return render(request, 'sales/product_form.html', {'form': form})

@user_passes_test(staff_check)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'sales/product_form.html', {'form': form, 'edit': True, 'product': product})

@user_passes_test(staff_check)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'sales/product_delete.html', {'product': product})

from django.db.models import Prefetch 

@login_required
@user_passes_test(staff_check)
def order_list(request):
    orders = OrderDetail.objects.all().order_by('created_at')

    paginator = Paginator(orders, 1000)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    return render(request, 'sales/order_list.html', {'orders': orders})

@login_required
@user_passes_test(staff_check)
def order_detail(request, order_code):
    order = get_object_or_404(OrderDetail, order_code=order_code)
    return render(request, 'sales/order_detail.html', {'order': order})

from django.contrib import messages

@login_required
@require_http_methods(["GET", "POST"])
@csrf_exempt
@user_passes_test(staff_check)
def order_create(request):
    if request.method == 'POST':
        try:
            # Phân tích dữ liệu JSON từ request body
            data = json.loads(request.body)
            order_code = data.get('order_code')
            customer_name = data.get('customer_name')
            created_at = data.get('created_at')
            products = data.get('products', [])
            quantities = data.get('quantities', [])

            if not order_code or not customer_name or not products or not quantities:
                return JsonResponse({'success': False, 'message': 'Please fill in all required fields.'})

            customer, created = Customer.objects.get_or_create(name=customer_name)
            total_price = 0

            with transaction.atomic():
                for product_id, quantity in zip(products, quantities):
                    product = get_object_or_404(Product, id=product_id)
                    line_total_price = product.price * int(quantity)
                    total_price += line_total_price

                    OrderDetail.objects.create(
                        order_code=order_code,
                        customer=customer,
                        product=product,
                        created_at=created_at,
                        quantity=int(quantity),
                        total_price=line_total_price
                    )

            return JsonResponse({'success': True, 'message': 'Order created successfully!'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

    else:
        products = Product.objects.all()
        return render(request, 'sales/order_form.html', {
            'products': products,
            'edit': False
        })

@user_passes_test(staff_check)
def order_edit(request, pk):
    order_detail = get_object_or_404(OrderDetail, pk=pk)
    if request.method == 'POST':
        form = OrderDetailForm(request.POST, instance=order_detail)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated successfully!')
            return redirect('order_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = OrderDetailForm(instance=order_detail)
        
    products = Product.objects.all()
    
    return render(request, 'sales/order_form.html', {'form': form, 'products':products, 'edit': True})

@user_passes_test(staff_check)
def order_delete(request, pk):
    order = get_object_or_404(OrderDetail, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('order_list')
    return render(request, 'sales/order_delete.html', {'order': order})

@login_required
@user_passes_test(staff_check)
def search_product_customers(request, product_id):
    product = Product.objects.get(id=product_id)
    orders = OrderDetail.objects.filter(product=product)
    customers = set(order.customer for order in orders)
    return render(request, 'sales/search_product_customers.html', {
        'product': product,
        'customers': customers,
        'orders': orders
    })

@login_required
@user_passes_test(staff_check)
def search_customer_orders(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    orders = OrderDetail.objects.filter(customer=customer)
    products = set(order.product for order in orders)
    return render(request, 'sales/search_customer_orders.html', {
        'customer': customer,
        'products': products,
        'orders': orders
    })


@login_required
@user_passes_test(staff_check)
def search_orders_by_product(request):
    products = Product.objects.all()
    return render(request, 'sales/search_orders_by_product.html', {
        'products': products
    })


@login_required
@user_passes_test(staff_check)
def search_orders_by_customer(request):
    customers = Customer.objects.all()
    return render(request, 'sales/search_orders_by_customer.html', {
        'customers': customers
    })

import csv
from django.contrib import messages
from .forms import UploadFileForm
from django.utils.dateparse import parse_datetime
from django.db import transaction, IntegrityError

# Ánh xạ tên cột CSV tiếng Việt sang tên trường trong cơ sở dữ liệu
column_mapping = {
    'Thời gian tạo đơn': 'created_at',
    'Mã đơn hàng': 'order_code',
    'Mã khách hàng': 'customer_code',
    'Tên khách hàng': 'customer_name',
    'Mã PKKH': 'segment_code',
    'Mô tả Phân Khúc Khách hàng': 'segment_description',
    'Mã nhóm hàng': 'group_code',
    'Tên nhóm hàng': 'group_name',
    'Mã mặt hàng': 'product_code',
    'Tên mặt hàng': 'product_name',
    'SL': 'quantity',
    'Đơn giá': 'price',
    'Thành tiền': 'total_price'
}

def handle_uploaded_file(file):
    file_data = file.read().decode('utf-8').splitlines()  # Đọc và giải mã file
    reader = csv.DictReader(file_data)
    
    for row in reader:
        data = {column_mapping[key]: value for key, value in row.items() if key in column_mapping}

        # Kiểm tra các giá trị bắt buộc
        if not data['customer_code'] or not data['product_code'] or not data['order_code']:
            continue  # Bỏ qua dòng nếu thiếu thông tin bắt buộc

        if not data['segment_code']:
            data['segment_code'] = 'DEFAULT_SEGMENT_CODE'  # Thay thế bằng giá trị mặc định nếu cần

        if not data['segment_description']:
            data['segment_description'] = 'DEFAULT_SEGMENT_DESCRIPTION'  # Thay thế bằng giá trị mặc định nếu cần
        
        if not data['price']:
            data['price'] = 0
        # Tạo hoặc lấy khách hàng
        customer, created = Customer.objects.get_or_create(
            customer_code=data['customer_code'],
            defaults={
                'name': data['customer_name'],
                'segment_code': data['segment_code'],
                'segment_description': data['segment_description']
            }
        )

        # Tạo hoặc lấy sản phẩm
        product, created = Product.objects.get_or_create(
            product_code=data['product_code'],
            defaults={
                'product_name': data['product_name'],
                'group_code': data['group_code'],
                'group_name': data['group_name'],
                'price': data['price']
            }
        )

        # Sử dụng transaction để đảm bảo an toàn khi thực hiện nhiều thao tác trên cơ sở dữ liệu
        try:
            with transaction.atomic():
                order_detail = OrderDetail.objects.filter(
                    order_code=data['order_code'],
                    customer=customer,
                    product=product
                ).first()

                if order_detail:
                    # Nếu có bản ghi, cập nhật bản ghi đó
                    order_detail.created_at = parse_datetime(data['created_at'])
                    order_detail.quantity = data['quantity']
                    order_detail.total_price = data['total_price']
                    order_detail.save()
                else:
                    # Nếu không có bản ghi, tạo mới
                    OrderDetail.objects.create(
                        order_code=data['order_code'],
                        customer=customer,
                        product=product,
                        created_at=parse_datetime(data['created_at']),
                        quantity=data['quantity'],
                        total_price=data['total_price']
                    )
        except IntegrityError as e:
            print(f"Error saving order: {e}")
            continue  # Bỏ qua dòng nếu có lỗi


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            messages.success(request, 'File uploaded successfully!')
            return redirect('upload_file')
    else:
        form = UploadFileForm()
    return render(request, 'sales/upload.html', {'form': form})

from django.contrib.auth import logout, login
from django.shortcuts import redirect

def login_view(request):
    if request.method == 'POST':
        login(request)
        return redirect('/sales')
    else:
        return redirect('/sales/')
    
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/sales/')
    else:
        return redirect('/sales/')
    
from rest_framework import viewsets
from .serializers import CustomerSerializer, ProductSerializer, OrderDetailSerializer
from rest_framework.decorators import action 
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class StatisticViewSets(viewsets.ViewSet):
    def list(self, request):
        customer_count = Customer.objects.count()
        product_count = Product.objects.count()
        order_count = OrderDetail.objects.count()
        data = {
            'Welcome Message': 'Welcome to the Sales Management System',
            'Developed By' : 'A website developed by Hang Nguyen',
            'Total Customers': customer_count,
            'Total Products': product_count,
            'Total Orders': order_count,
        }
        return Response(data)
    
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('id')[100:]
    serializer_class = CustomerSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer

class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all().order_by('-id')[100:]
    serializer_class = OrderDetailSerializer
        

from rest_framework.pagination import PageNumberPagination
from django.db.models import Prefetch

class CustomPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1

class SearchViewSet(viewsets.ViewSet):
    pagination_class = CustomPagination

    def list(self, request):
        return Response([])

    @action(detail=False, methods=['get'])
    def orders_by_product(self, request):
        products = Product.objects.filter().order_by('id')
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)

        result = []
        for product in paginated_products:
            product_data = {
                'id': product.id,
                'product_name': product.product_name,
                'product_code': product.product_code,
                'orders': []
            }

            orders = OrderDetail.objects.filter(product=product).select_related('customer').order_by('id')
            
            order_page = request.GET.get('order_page', 1)
            order_page_size = request.GET.get('order_page_size', 300)
            order_paginator = Paginator(orders, order_page_size)
            paginated_orders = order_paginator.get_page(order_page)

            
            for order in paginated_orders:
                order_data = {
                    'customer_name': order.customer.name,
                    'customer_code': order.customer.customer_code,
                    'order_code': order.order_code,
                    'created_at': order.created_at,
                    'quantity': order.quantity
                }
                product_data['orders'].append(order_data)

            product_data['orders_pagination'] = {
                'total_orders': order_paginator.count,
                'total_pages': order_paginator.num_pages,
                'current_page': paginated_orders.number,
                'has_next': paginated_orders.has_next(),
                'has_previous': paginated_orders.has_previous(),
            }
            result.append(product_data)
        return paginator.get_paginated_response(result)
    
    @action(detail=False, methods=['get'])
    def orders_by_customer(self, request):
        customers = Customer.objects.prefetch_related(
            Prefetch('orderdetail_set', queryset=OrderDetail.objects.select_related('product'))
        ).order_by('id')
        paginator = self.pagination_class()
        paginated_customers = paginator.paginate_queryset(customers, request)

        result = []
        for customer in paginated_customers:
            customer_data = {
                'id': customer.id,
                'name': customer.name,
                'customer_code': customer.customer_code,
                'orders': []
            }
            for order in customer.orderdetail_set.all():
                order_data = {
                    'product_name': order.product.product_name,
                    'product_code': order.product.product_code,
                    'order_code': order.order_code,
                    'created_at': order.created_at,
                    'quantity': order.quantity,
                    'total_price': order.total_price
                }
                customer_data['orders'].append(order_data)
            result.append(customer_data)
        
        return paginator.get_paginated_response(result)


from .models import Chat
from rest_framework.permissions import IsAuthenticated
from .serializers import ChatSerializer
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend # type: ignore



class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    filter_backends=[DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user']
    ordering_fields = ['timestamp']
    ordering =['-timestamp']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user) # Chỉ cho phép user xem tin nhắn của chính họ
    
def chat_view(request):
    chat = Chat.objects.all()
    context = {
        'chat': chat,
        'user': request.user
    }
    return render(request, 'sales/chat.html', {'chat': chat})

