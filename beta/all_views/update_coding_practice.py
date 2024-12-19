import time
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from models.models import ResourceLoadData
from utils.Beta.rename_zip import rename_json_files_in_zip
from utils.Beta.aws import set_aws_credentials
from utils.Beta.sheet_loading import submit_sheet_loading_request
from utils.Beta.task_details import get_task_details
from utils.Beta.unlock_resource import submit_unlock_resource
from utils.Beta.upload_to_s3 import upload_to_s3
from utils.Beta.delete_resource import delete_resource


@login_required
def update_resource_view(request, resource_id):
    """Display update options for a specific resource."""
    resource = get_object_or_404(ResourceLoadData, resource_id=resource_id, user=request.user)
    return render(request, 'Beta/update_coding_practice.html', {'resource': resource})



@login_required
@csrf_exempt
def update_process_step(request):
    """Process each step in updating the resource asynchronously."""
    step = request.POST.get('step')
    resource_id = request.POST.get('resource_id')
    resource = get_object_or_404(ResourceLoadData, resource_id=resource_id, user=request.user)
    response_data = {'status': 'success', 'step': step, 'message': ''}
    print("Entered!")
    try:
        if step == "delete_old_resource":
            delete_request_id = delete_resource(resource.resource_id)
            if not delete_request_id:
                return JsonResponse({'status': 'error', 'message': 'Failed to initiate delete resource request.'}, status=500)
            request.session['delete_request_id'] = delete_request_id
            response_data['message'] = "Delete resource request initiated. Checking status."

        elif step == "check_delete_status":
            task_status, exception_url = get_task_details(request.session['delete_request_id'])
            if task_status != "SUCCESS":
                return JsonResponse({'status': 'error', 'message': f'Delete task failed : {exception_url}'}, status=500)
            response_data['message'] = "Old resource deleted successfully."

        elif step == "rename_new_zip":
            zip_file = request.FILES.get('zip_file')
            if not zip_file:
                return JsonResponse({'status': 'error', 'message': 'No zip file provided.'}, status=400)
            result = rename_json_files_in_zip(zip_file, "media/output", resource.resource_id)
            if 'errors' in result:
                response_data['status'] = 'error'
                response_data['message'] = ["Error in JSON Files."] + result["errors"]
                response_data['errors'] = result["errors"]  # Include all errors for client-side display
                print(response_data['errors'])
                return JsonResponse(response_data)
            request.session['final_zip_path'] = result["zip_path"]
            response_data['message'] = "Renamed new zip file."


        elif step == "upload_s3":
            creds = set_aws_credentials()
            s3_file_url = upload_to_s3(cred=creds, file_path=request.session['final_zip_path'])
            if not s3_file_url:
                return JsonResponse({'status': 'error', 'message': 'Failed to upload new zip to S3.'}, status=500)
            request.session['s3_file_url'] = s3_file_url
            response_data['message'] = "Uploaded new zip to S3."

        elif step == "update_sheet_loading_json":
            final_json = {
                "spread_sheet_name": resource.spreadsheet_name,
                "data_sets_to_be_loaded": ["ResourcesData", "Units", "QuestionSet"],
                "question_set_questions_dir_path_url": request.session['s3_file_url'],
                "is_json_converted": False
            }
            sheet_loading_request_id = submit_sheet_loading_request(final_json)
            if not sheet_loading_request_id:
                return JsonResponse({'status': 'error', 'message': 'Failed to submit sheet loading request.'}, status=500)
            request.session['sheet_loading_request_id'] = sheet_loading_request_id
            response_data['message'] = "Updated sheet loading JSON and sent request."

        elif step == "check_task_status":
            task_status, exception_url = get_task_details(request.session['sheet_loading_request_id'])
            if task_status != "SUCCESS":
                return JsonResponse({'status': 'error', 'message': f'Sheet Loading failed : {exception_url}'}, status=500)
            response_data['message'] = "Sheet loading task completed."

        elif step == "unlock_resource":
            unlock_request_id = submit_unlock_resource(resource.resource_id)
            if not unlock_request_id:
                return JsonResponse({'status': 'error', 'message': 'Failed to unlock resource.'}, status=500)
            resource.unlock_request_id = unlock_request_id
            response_data['message'] = "Resource unlocked successfully."

        elif step == "save_to_db":
            resource.file_url = request.session.get('s3_file_url')
            resource.sheet_loading_request_id = request.session.get('sheet_loading_request_id')
            resource.update_time = now()
            resource.save()
            response_data['message'] = "Database updated with new resource details."
            response_data['complete'] = True

        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid step provided.'}, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)

    return JsonResponse(response_data)
