from django.contrib import admin

# Register your models here.
from .models import Customer, Product, OrderDetail, Chat
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)
admin.site.register(OrderDetail)
admin.site.register(Chat)


