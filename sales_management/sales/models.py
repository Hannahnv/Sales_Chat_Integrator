from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    customer_code = models.TextField(unique=True)
    name = models.CharField(max_length=100)
    segment_code = models.TextField()
    segment_description = models.TextField()
    
    def __str__(self):
        return self.name

class Product(models.Model):
    product_code = models.CharField(max_length=6, unique=True)
    product_name = models.CharField(max_length=100)
    group_code = models.TextField()
    group_name = models.CharField(max_length=100)
    price = models.IntegerField()
    
    def __str__(self):
        return self.product_name
    
class OrderDetail(models.Model):
    order_code = models.CharField(max_length=10)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    quantity = models.IntegerField()
    total_price = models.IntegerField()
    
    def __str__(self):
        return f'Order: {self.order_code} - Product: {self.product.product_name}'
    
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.message}"
    class Meta:
        ordering = ['-timestamp']
        