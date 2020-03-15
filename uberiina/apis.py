import json
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from oauth2_provider.models import AccessToken
from .models import Restaurant, Meal, Order, OrderDetails
from .serializer import RestaurantSerializer, MealSerializer, OrderSerializer
from django.views.decorators.csrf import csrf_exempt
import stripe
from config.settings import STRIPE_SECRET_KEY
# from config.local_settings import STRIPE_SECRET_KEY
# Stripe API用のシークレットキー取得
stripe.api_key = STRIPE_SECRET_KEY


# レストランデータ取得
def customer_get_restaurants(request):
    restaurants = RestaurantSerializer(
        Restaurant.objects.all().order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"restaurants": restaurants})


#　料理データ取得
def customer_get_meals(request, restaurant_id):
    meals = MealSerializer(
        Meal.objects.filter(restaurant_id = restaurant_id).order_by('-id'),
        many = True,
        context = {'request': request},
    ).data

    return JsonResponse({'meals': meals})


# カスタマー：オーダー作成
@csrf_exempt
def customer_add_order(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token= request.POST.get('access_token'), expires__gt=timezone.now())
        customer = access_token.user.customer

        if Order.objects.filter(customer = customer).exclude(status= Order.DELIVERED):
            return JsonResponse({'status': 'failed', 'error': 'Your last order must be completed!!'})

        if not request.POST['address']:
            return JsonResponse({'status': 'failed', 'error': 'Addres is required!!'})
     
        order_details = json.loads(request.POST["order_details"])
        
        order_total = 0
        for meal in order_details:
            order_total += Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]

        if len(order_details) > 0:
            order = Order.objects.create(
                customer = customer,
                restaurant_id = request.POST["restaurant_id"],
                total = order_total,
                status = Order.COOKING,
                address = request.POST["address"]
            )

            for meal in order_details:
                OrderDetails.objects.create(
                    order = order,
                    meal_id = meal["meal_id"],
                    quantity = meal["quantity"],
                    sub_total = Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]
                )
            return JsonResponse({"status": "success"})

        else:
            return JsonResponse({"status": "failed", "error": "Failed connect to Stripe."})
            

# カスタマー：最新のオーダー情報取得
def customer_get_latest_order(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    customer = access_token.user.customer
    order = OrderSerializer(
        Order.objects.filter(customer = customer).last()
    ).data

    return JsonResponse({"order": order})


# カスタマー：ドライバーの位置情報取得
@csrf_exempt
def customer_driver_location(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    customer = access_token.user.customer
    current_order = Order.objects.filter(customer = customer, status = Order.DELIVERED).last()
    location = current_order.driver.location

    return JsonResponse({"location": location})


# レストラン：未チェックオーダーの通知表示
def restaurant_order_notification(request, last_request_time):
    notification = Order.objects.filter(restaurant = request.user.restaurant,
        created_at__gt = last_request_time).count()

    return JsonResponse({"notification": notification})


# ドライバー：配達が可能なオーダー情報取得
def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status=Order.READY, driver=None).order_by('-id'),
        many = True
    ).data
    return JsonResponse({'orders': orders})


# ドライバー：配達するオーダーを決定
@csrf_exempt
def driver_pick_order(request):
    if request.method == 'POST':
        access_token =  AccessToken.objects.get(token=request.POST.get('access_token'), expires__gt=timezone.now())
        driver = access_token.user.driver
        if Order.objects.filter(driver=driver).exclude(status=Order.ONTHEWAY):
            return JsonResponse({'status': 'failed', 'error': 'You can only pick one order at the same time.'})
        
        # 配達中じゃない場合、オーダーを更新
        try:
            order = Order.objects.get(
                id = request.POST['order_id'],
                driver = None,
                status = Order.READY,
            )
            
            order.driver = driver
            order.status = Order.ONTHEWAY
            order.picked_at = timezone.now()
            order.save()
            return JsonResponse({'status': 'success'})

        # 配達中ではないが、対象のオーダーが存在しない場合
        except Order.DoesNotExist:
            return JsonResponse({'status': 'failed', 'error': 'This order has been picked up by another.'})

    return JsonResponse({})


# ドライバー：最新の配達情報
def driver_get_latest_order(request):
    access_token = AccessToken.objects.get(token=request.GET.get('access_token'), expires__gt=timezone.now())
    driver = access_token.user.driver
    order = OrderSerializer(
        Order.objects.filter( driver=driver).order_by('picked_at').last()
    ).data
    
    return JsonResponse({'order': order})


# ドライバー：配達の完了
@csrf_exempt
def driver_complete_order(request):
    access_token = AccessToken.objects.get(token=request.POST.get('access_token'), expires__gt=timezone.now())
    driver = access_token.user.driver
    order = Order.objects.get(id=request.POST['order_id'], driver=driver)
    order.status = Order.DELIVERED
    order.save()
    return JsonResponse({'status': 'success'})


# ドライバー：収入情報取得
def driver_get_revenue(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())
    driver = access_token.user.driver
    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        orders = Order.objects.filter(
            driver = driver,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )

        revenue[day.strftime("%a")] = sum(order.total for order in orders)

    return JsonResponse({"revenue": revenue})


# ドライバー：自身の位置情報更新
@csrf_exempt
def driver_update_location(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        driver = access_token.user.driver

        # Set location string => database
        driver.location = request.POST["location"]
        driver.save()

        return JsonResponse({"status": "success"})