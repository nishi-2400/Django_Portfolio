from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Restaurant, Meal, Order, OrderDetails, Customer, Driver
from .serializer import RestaurantSerializer, CustomerSerializer, DriverSerializer
from rest_framework import viewsets
from .forms import UserSignupForm, UserEditForm, RestaurantSignupForm, ResraurantMealForm
from django.core.paginator import Paginator
from django.db.models import Sum, Count, When, Case


"""""""""
Home
"""""""""
def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


"""""""""
Restaurant
"""""""""
# Restaurant Home
@login_required
def restaurant_home(request):
    return render(request, 'restaurant/order.html')

# Restaurnt Account Show/Edit
@login_required
def restaurant_account(request):
    user_form = UserEditForm(instance=request.user)
    restaurant_form = RestaurantSignupForm(instance=request.user.restaurant)
    params = {
        'restaurant_form': restaurant_form,
        'user_form': user_form
    }
    
    if request.method == 'POST':
        edited_user_data = UserEditForm(request.POST, instance=request.user)
        edited_restaurant_data = RestaurantSignupForm(request.POST, request.FILES, instance=request.user.restaurant)
        
        if edited_user_data.is_valid() and edited_restaurant_data.is_valid():
            edited_user_data.save()
            edited_restaurant_data.save()
            messages.success(request, '登録内容を変更しました。')
            return redirect(to='/restaurant/account')

    return render(request, 'restaurant/account.html', params)


# Restaurant Signup
def restaurant_signup(request):
    user_form = UserSignupForm()
    restaurant_form = RestaurantSignupForm()
    params = {
        'user_form': user_form,
        'restaurant_form': restaurant_form,
    }

    if request.method == 'POST':
        new_user_data = UserSignupForm(request.POST)
        new_restaurant_data = RestaurantSignupForm(request.POST, request.FILES)

        if new_user_data.is_valid() and new_restaurant_data.is_valid():
            new_user_obj = User.objects.create_user(**new_user_data.cleaned_data)
            new_restaurant_obj = new_restaurant_data.save(commit=False)
            new_restaurant_obj.user = new_user_obj
            # デフォルトのロゴを設定
            new_restaurant_obj.logo = 'restaurant_logo1.jpg'
            new_restaurant_obj.save()
            # アカウント本登録用のメール送信（予定）
            messages.success(request, 'Welcome!! アカウントを作成しました！')
            # send_notification('アカウント登録ありがとうございます。')
            return redirect(to='/accounts/login')

    return render(request, 'restaurant/signup.html', params)


# Meal List
@login_required
def restaurant_meal(request):
    if request.method == 'POST':
        keyword = request.POST['keyword']
        search_meals_data = Meal.objects.filter(name__contains=keyword, restaurant=request.user.restaurant)
        meal_paginator = Paginator(search_meals_data, 3)
        meal_page = meal_paginator.get_page(request.GET.get('page'))
        params = {
            'meal_page': meal_page,

        }
        return render(request, 'restaurant/meal.html', params)

    # ページネーション
    meal_list = Meal.objects.filter(restaurant=request.user.restaurant)
    meal_paginator = Paginator(meal_list, 3)
    meal_page = meal_paginator.get_page(request.GET.get('page'))
    params = {
        'meal_page': meal_page,
    }
    return render(request, 'restaurant/meal.html', params)

# Meal add
@login_required
def restaurant_meal_add(request):
    if request.method == 'POST':
        new_meal_data = ResraurantMealForm(request.POST, request.FILES)
        if new_meal_data.is_valid():
            new_meal_obj = new_meal_data.save(commit=False)
            new_meal_obj.restaurant = request.user.restaurant
            new_meal_obj.save()
            messages.success(request, '登録内容を保存しました。')
            return redirect(to='/restaurant/meal')
        else:
            messages.error(request, '登録内容にエラーがあります。')

    meal_form = ResraurantMealForm()
    params = {
        'meal_form': meal_form
    }
    return render(request, 'restaurant/add.html', params)

# Meal Edit
@login_required
def restaurant_meal_edit(request, meal_id):
    if request.method == 'POST':
        edited_meal_data = ResraurantMealForm(request.POST, request.FILES, instance=Meal.objects.get(id=meal_id))
        if edited_meal_data.is_valid():
            edited_meal_data.save()
            messages.success(request, '登録内容を更新しました。')
            return redirect(to='/restaurant/meal')
        else:
            messages.error(request, '登録内容にエラーがあります。')

    meal_form = ResraurantMealForm(instance=Meal.objects.get(id=meal_id))
    params = {
        'meal_form': meal_form,
        'meal_id': meal_id,
    }
    return render(request, 'restaurant/edit.html', params)


# Meal Delete
@login_required
def restaurant_meal_delete(request, meal_id):
    target_meal_data = Meal.objects.get(id=meal_id)
    target_meal_data.delete()
    messages.success(request, '登録内容を削除しました。')
    return redirect(to='/restaurant/meal')


# Order List
@login_required
def restaurant_order(request):
    if request.method == 'POST':
        order = Order.objects.get(id=request.POST['id'], restaurant=request.user.restaurant)
        if order.status == Order.COOKING:
            order.status = Order.READY
            order.save()

    orders = Order.objects.filter(restaurant=request.user.restaurant)
    params = {
        'orders': orders
    }
    return render(request, 'restaurant/order.html', params)


# Report
@login_required
def restaurant_report(request):
    # 今日の日付を取得
    today = datetime.now()
    # 今日の曜日を取得（月〜日：０〜７）
    weekdays = today.weekday()
    # 今週の月曜日の日付を取得
    start_date = today - timedelta(days=weekdays)
    # 今週の月曜日から今日までの日付格納するリスト
    target_days = []
    # 今週の月曜日から今日までの各曜日の売上合計を格納するリスト
    weekly_sales = []
    # 今週の月曜日から今日までの注文数合計を格納するリスト
    weekly_orders = []
    # 今日が月曜日ではない場合
    if weekdays != 0:
        # 月曜日から今日までの日付を取得する
        target_days = [start_date + timedelta(days=i) for i in range(weekdays+1)]
        # for i in range(weekdays+1):
        #     target_days.append(start_date + timedelta(days=i))
    # 今日が月曜日の場合
    else:
        target_days.append(start_date)
    
    # 各曜日のオーダーを取得
    for target_day in target_days:
        daily_orders = Order.objects.filter(
            restaurant=request.user.restaurant,
            status=Order.DELIVERED, 
            created_at__year=target_day.year, 
            created_at__month=target_day.month, 
            created_at__day=target_day.day,
        )
        # 1日の売上を初期化
        daily_sales = 0
        # 1日の売上を集計
        for order in daily_orders:
            daily_sales += order.total
        # 各曜日の売上の合計をリストに格納
        weekly_sales.append(daily_sales)
        # 各曜日の注文数の合計をリストに格納
        weekly_orders.append(daily_orders.count())

    # トップ３の料理の算出
    top_3_meals = Meal.objects.filter(restaurant=request.user.restaurant).annotate(total_order = Sum('orderdetails__quantity')).order_by('-total_order')[:3]
    meal_data = {
        'labels': [meal.name for meal in top_3_meals],
        'data': [meal.total_order or 0 for meal in top_3_meals],
    }

    # トップ３のドライバー算出
    top_3_drivers =  Driver.objects.annotate(
        total_order=Count(
            Case (
                When(order__restaurant=request.user.restaurant, then=1)
            )
        )
    ).order_by('-total_order')[:3]

    driver_data = {
        'labels': [driver.user.get_full_name() for driver in top_3_drivers],
        'data': [driver.total_order for driver in top_3_drivers],
    }
    
    params = {
        'weekly_sales': weekly_sales,
        'weekly_orders': weekly_orders,
        'meal_data': meal_data,
        'driver_data': driver_data 
    }

    return render(request, 'restaurant/report.html', params)
    

# serializer用のViewset
class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    queryset = Restaurant.objects.all()

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

class DriverViewSet(viewsets.ModelViewSet):
    serializer_class = DriverSerializer
    queryset = Driver.objects.all()
    
    