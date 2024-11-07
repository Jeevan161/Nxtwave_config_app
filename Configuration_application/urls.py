"""
URL configuration for Configuration_application project.

The `urlpatterns` list routes URLs to all_views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function all_views
    1. Add an import:  from my_app import all_views
    2. Add a URL to urlpatterns:  path('', all_views.home, name='home')
Class-based all_views
    1. Add an import:  from other_app.all_views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

import accounts

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('beta/', include('beta.urls'))
]
