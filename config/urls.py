
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from uberiina.urls import router as uber_iina_router
# from .urls import router as uber_iina_router
from django.contrib.staticfiles.urls import static
from . import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    # 認証
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # アプリ
    path('', include('uberiina.urls')),
    # path('', include('foodtasker.urls')),
    # API
    path('api/', include(uber_iina_router.urls), name='api'),
    # Django REST Framework Social OAuth2
    path('api/social/', include('rest_framework_social_oauth2.urls')),
]
# 画像ファイル用URLパターン
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)