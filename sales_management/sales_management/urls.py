from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sales/', include('sales.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('sales/api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('sales/api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^.*', TemplateView.as_view(template_name='index.html')),  # Phục vụ React app
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
