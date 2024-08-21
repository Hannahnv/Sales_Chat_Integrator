from rest_framework import serializers
from .models import Customer, Product, OrderDetail, Chat

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Hiển thị tên người dùng thay vì ID
    
    class Meta:
        model = Chat
        fields = ['id', 'user', 'message', 'timestamp']
        read_only_fields = ['user', 'timestamp']  # Ngăn chặn việc chỉnh sửa những trường này