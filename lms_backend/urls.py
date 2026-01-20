from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Accounts API endpoints
    path('api/accounts/', include('accounts.urls')),
]
