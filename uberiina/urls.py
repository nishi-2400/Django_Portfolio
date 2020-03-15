from django.urls import path, include
from django.conf.urls import url
from uberiina import views, apis
from rest_framework import routers
from .views import RestaurantViewSet, CustomerViewSet, DriverViewSet

app_name = 'uberiina'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    path('about', views.about, name='about'),

    # Restaurant
    path('restaurant', views.restaurant_order, name='restaurant-home'),
    path('restaurant/signup', views.restaurant_signup, name='restaurant-signup'),
    path('restaurant/account', views.restaurant_account, name='restaurant-account'),
    path('restaurant/meal', views.restaurant_meal, name='restaurant-meal'),
    path('restaurant/meal/add', views.restaurant_meal_add, name='restaurant-meal-add'),
    path('restaurant/meal/edit/<int:meal_id>', views.restaurant_meal_edit, name='restaurant-meal-edit'),
    path('restaurant/meal/delete/<int:meal_id>', views.restaurant_meal_delete, name='restaurant-meal-delete'),
    path('restaurant/order', views.restaurant_order, name='restaurant-order'),
    path('restaurant/report', views.restaurant_report, name='restaurant-report'),
    path('api/restaurant/order/notification/<last_request_time>/', apis.restaurant_order_notification),

    # API
    path('api/customer/restaurants', apis.customer_get_restaurants),
    path('api/customer/meals/<int:restaurant_id>', apis.customer_get_meals),
    path('api/customer/order/add', apis.customer_add_order, name='api-customer-order-add'),
    path('api/customer/order/latest', apis.customer_get_latest_order),
    path('api/customer/driver/location', apis.customer_driver_location),
    
    # API For Driver
    path('api/driver/orders/ready', apis.driver_get_ready_orders),
    path('api/driver/order/pick', apis.driver_pick_order),
    path('api/driver/order/latest', apis.driver_get_latest_order),
    path('api/driver/order/complete', apis.driver_complete_order),
    path('api/driver/location/update', apis.driver_update_location),
    path('api/driver/revenue', apis.driver_get_revenue),
]

router = routers.DefaultRouter()
router.register('Restaurant', RestaurantViewSet)
router.register('Customer', CustomerViewSet)
router.register('Driver', DriverViewSet)

