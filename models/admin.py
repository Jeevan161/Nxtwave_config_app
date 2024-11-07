from django.contrib import admin
from .models import ResourceLoadData

@admin.register(ResourceLoadData)
class ResourceLoadDataAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_id', 'topic_id', 'user', 'status', 'resource_type', 'updated_count', 'time_loaded', 'update_time', 'processing_duration')
    search_fields = ('title', 'resource_id', 'topic_id')
    list_filter = ('status', 'resource_type', 'time_loaded')
    ordering = ('-time_loaded',)
    readonly_fields = ('time_loaded', 'update_time')

# If you want to register without customizations:
# admin.site.register(ResourceLoadData)
