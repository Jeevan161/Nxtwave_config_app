from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from models.models import ResourceLoadData

@login_required
def user_loading_records(request):
    # Fetch all ResourceLoadData records for the logged-in user
    user_records = ResourceLoadData.objects.filter(user=request.user).order_by('-time_loaded')  # Replace with 'time_loaded'

    # Pass these records to the template
    return render(request, 'Beta/my_loadings.html', {'user_records': user_records})
