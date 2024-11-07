from django.db import models
from django.contrib.auth.models import User


class ResourceLoadData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    resource_id = models.CharField(max_length=100, unique=True)
    topic_id = models.CharField(max_length=100)
    child_order = models.IntegerField()
    spreadsheet_name = models.CharField(max_length=255)
    spreadsheet_id = models.CharField(max_length=100)
    sheet_loading_request_id = models.CharField(max_length=100)
    unlock_request_id = models.CharField(null=True,max_length=100)
    file_url = models.URLField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=50)
    updated_count = models.IntegerField(default=0)
    time_loaded = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    # New field to track processing duration
    processing_duration = models.FloatField(null=True, blank=True)  # Duration in seconds

    def __str__(self):
        return f"{self.title} - {self.resource_id}"
