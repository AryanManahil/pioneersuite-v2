from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view  # ✅ custom view import
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Use custom login view
    path('accounts/login/', login_view, name='login'),

    # ✅ Keep using default logout
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # App routes
    path('', include('home.urls')),
    path('users/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('purchase/', include(('purchase.urls', 'purchase'), namespace='purchase')),
    path('settings/', include('core_settings.urls', namespace='core_settings')),
    path('digitalinsurance/', include('digitalinsurance.urls', namespace='digitalinsurance')),
    path('edocuments/', include('edocuments.urls', namespace='edocuments')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
