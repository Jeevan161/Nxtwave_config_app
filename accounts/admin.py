from django.contrib import admin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin


class UserAdmin(ModelAdmin):
    list_display = ['username', 'email', 'is_active', 'is_staff']
    list_editable = ['is_active', 'is_staff']


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
