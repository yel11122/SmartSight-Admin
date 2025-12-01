"""
URL configuration for admin_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django's built-in admin site
    path('admin/', admin.site.urls),

    # I-apil ang imong admin_panel URLs ubos sa 'api/'
    path('api/', include('admin_panel.urls')),

    # This is for the admin panel views, if you need them.
    # Note: If your admin_panel.urls handles everything, this might be redundant.
    # But for safety, we'll keep it for now.
    path('', include('admin_panel.urls')),
]
