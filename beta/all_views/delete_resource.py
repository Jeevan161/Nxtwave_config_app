from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from models.models import ResourceLoadData
from utils.Beta.delete_resource import delete_resource  # Imported function causing conflict
from utils.Beta.task_details import get_task_details


@login_required
@require_POST
def delete_resource_view(request, resource_id):
    """Delete a specific resource."""
    try:
        # Step 1: Validate input and retrieve the resource object
        print(f"Received delete request for resource_id: {resource_id}")

        # Ensure resource_id is a valid string or UUID and retrieve the resource
        resource = get_object_or_404(ResourceLoadData, resource_id=resource_id, user=request.user)
        print(f"Resource found: {resource}")

        # Step 2: Initiate the delete request
        delete_request_id = delete_resource(resource.resource_id)
        print(f"Delete Request ID: {delete_request_id}")

        # Check if delete_request_id is not None or empty
        if not delete_request_id or not isinstance(delete_request_id, str):
            return JsonResponse({'status': 'error', 'message': 'Failed to initiate delete resource request.'}, status=500)

        # Step 3: Check the status of the delete request
        task_status, exception = get_task_details(delete_request_id)
        print(f"Task Status: {task_status}, Exception: {exception}")

        # Step 4: Handle the result based on task_status
        if task_status == 'SUCCESS':
            resource.delete()
            return JsonResponse({'status': 'success', 'message': 'Resource deleted successfully.'})
        elif task_status == 'FAILED':
            return JsonResponse({'status': 'error', 'message': f'Failed to delete resource: {exception}'}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Unexpected task status: ' + task_status}, status=500)

    except ResourceLoadData.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Resource not found.'}, status=404)

    except Exception as e:
        # More detailed error response
        print(f"An unexpected error occurred: {str(e)}")
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)
