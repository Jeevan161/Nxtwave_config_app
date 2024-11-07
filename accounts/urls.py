from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home_redirect'),
    path('register', views.register_view, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('content_developer', views.content_developer_dashboard, name='content_developer_dashboard'),
    path('configurator', views.configurator_dashboard, name='configurator_dashboard'),
    path('beta/dashboard/', views.beta_dashboard, name='beta_dashboard'),
    path('gamma-dashboard/', views.gamma_dashboard, name='gamma_dashboard'),
    path('access-denied/', views.access_denied, name='access_denied'),

]
