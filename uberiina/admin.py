from django.contrib import admin
from .models import Restaurant, Meal, Order, OrderDetails, Customer, Driver

# 管理画面への登録（表示）
admin.site.register(Restaurant)
admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(OrderDetails)
admin.site.register(Customer)
admin.site.register(Driver)