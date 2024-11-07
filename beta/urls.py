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
from .all_views.coding_practice import coding_practice_view,process_step
import accounts
from .all_views.my_loadings import user_loading_records
from .all_views.update_coding_practice import update_resource_view, update_process_step

urlpatterns = [
    path('coding-practice',coding_practice_view,name="coding_practice_submit"),
    path('my-loadings',user_loading_records,name="my-loadings"),
    path('coding-practice/process-step/', process_step, name='process_step'),
    path('update/<str:resource_id>/', update_resource_view, name='update_resource'),
    path('/beta/update/process-step/', update_process_step, name='update_process_step'),
]
