import logging
from celery import shared_task
from sales.models import Customer, Product, OrderDetail
from django.contrib.auth.models import User
import re
from django.utils import timezone
from django.db.models import Q, Max

logger = logging.getLogger(__name__)

def generate_order_code():
    last_order_code = OrderDetail.objects.aggregate(Max('order_code'))['order_code__max']
    if last_order_code:
        num = int(last_order_code[3:]) + 1
    else:
        num = 1
    return f'ORD{num:07d}'

@shared_task
def process_chat_message(message, username):
    if re.search(r'\b(đặt hàng|mua).*(\d+\s+\w+(\s+\w+)*(\s+(và|,)\s+)?)+', message, re.IGNORECASE):
        return process_order(message, username)
    elif re.search(r'\b(xem|kiểm tra|lấy)\s+lịch sử\s+(mua hàng|đặt hàng)\b', message, re.IGNORECASE):
        return get_order_history(username)
    elif re.search(r'\b(Hi|Hello|xin chào)\b', message, re.IGNORECASE):
        return "Xin chào, tôi có thể giúp gì cho bạn?"
    else:
        return "Xin lỗi, tôi không hiểu yêu cầu của bạn. Bạn có thể đặt hàng hoặc xem lịch sử mua hàng."

@shared_task
def process_order(message, username):
    products = re.findall(r'(\d+)\s+([\w\s]+?)(?:,|\s+và\s+|$)', message)
    logger.debug(f"Parsed products from message: {products}")
    
    if not products:
        return "Không tìm thấy sản phẩm nào trong yêu cầu đặt hàng của bạn."
    
    order_details = []
    total_price = 0
    not_found_products = []

    try:
        user = User.objects.get(username=username)
        customer, created = Customer.objects.get_or_create(user=user, defaults={'name': user.get_full_name() or user.username})
    except User.DoesNotExist:
        return "Không tìm thấy người dùng."

    order_code = generate_order_code()

    for quantity, product_name in products:
        try:
            product = Product.objects.filter(
                Q(product_name__icontains=product_name.strip()) |
                Q(product_name__icontains=product_name.strip().replace(' ', ''))
            ).first()
            
            if product is None:
                not_found_products.append(product_name.strip())
                continue
            
            quantity = int(quantity)
            price = product.price * quantity
            total_price += price
            
            order_detail = OrderDetail(
                order_code=order_code,
                product=product,
                quantity=quantity,
                total_price=price,
                customer=customer,
                created_at=timezone.now()
            )
            order_detail.save()
            order_details.append(order_detail)
        except Exception as e:
            logger.error(f"Lỗi khi xử lý sản phẩm {product_name}: {str(e)}")
            not_found_products.append(product_name.strip())
    
    if not order_details:
        return f"Không tìm thấy sản phẩm: {', '.join(not_found_products)}"
    
    response = f"Đơn hàng của bạn đã được đặt thành công. Mã đơn hàng: {order_code}. Tổng giá trị đơn hàng: {total_price:,} VND.\n"
    
    response += "Chi tiết đơn hàng:\n"
    for order in order_details:
        response += f"- {order.product.product_name}: {order.quantity} x {order.product.price:,} VND = {order.total_price:,} VND.\n"
    
    if not_found_products:
        response += f"\nKhông tìm thấy các sản phẩm sau: {', '.join(not_found_products)}"
    
    return response

@shared_task
def get_order_history(username):
    try:
        user = User.objects.get(username=username)
        customer = Customer.objects.get(user=user)
    except (User.DoesNotExist, Customer.DoesNotExist):
        return "Không tìm thấy khách hàng."
    
    orders = OrderDetail.objects.filter(customer=customer).order_by('-created_at')
    
    if not orders:
        return "Bạn chưa có lịch sử mua hàng nào."
    
    history = []
    for order in orders:
        local_time = timezone.localtime(order.created_at)
        history.append(
            f"Mã đơn hàng: {order.order_code},\n"
            f"Tên khách hàng: {order.customer.name},\n"
            f"Sản phẩm: {order.product.product_name},\n"
            f"Ngày tạo đơn: {local_time.strftime('%d/%m/%Y, %I:%M %p')},\n"
            f"Số lượng: {order.quantity},\n"
            f"Tổng tiền: {order.total_price} VND.\n"
        )
    
    return "\n".join(history)
