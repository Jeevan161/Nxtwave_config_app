import json
import os
import time
import uuid
import zipfile

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from models.models import ResourceLoadData
from utils.Beta.rename_zip import rename_json_files_in_zip
from utils.Beta.aws import set_aws_credentials
from utils.Beta.sheet_loading import submit_sheet_loading_request
from utils.Beta.sheet_preparation import upload_to_google_sheets
from utils.Beta.task_details import get_task_details
from utils.Beta.unlock_resource import submit_unlock_resource
from utils.Beta.upload_to_s3 import upload_to_s3
from utils.Beta.mcq_json_preparation import mcq_practice_prepare_json


@login_required
def mcq_practice_view(request):
    if request.method == 'GET':
        return render(request, 'Beta/mcq_practice.html')


@login_required
@csrf_exempt
def mcq_process_step(request):
    """Processes each step asynchronously based on the `step` parameter from the request."""
    step = request.POST.get('step')
    get_task_details("7c2cefad-6f69-4387-ad2a-0d4f1c7f259a")
    response_data = {'status': 'success', 'step': step, 'message': ''}

    if step == "initialize":
        request.session['resource_id'] = str(uuid.uuid4())
        response_data['message'] = "Initialized process."

    elif step == "rename_json":
        zip_file = request.FILES.get('zip_file')
        resource_id = request.session['resource_id']
        output_dir = "media/output"

        # Call the updated rename_json_files_in_zip function
        result = rename_json_files_in_zip(zip_file, output_dir, resource_id)

        # Check for validation errors
        if 'errors' in result:
            response_data['status'] = 'error'
            response_data['message'] = ["Error in JSON Files."] +  result["errors"]
            response_data['errors'] = result["errors"]  # Include all errors for client-side display
            print(response_data['errors'])
            return JsonResponse(response_data)

        # If no errors, store the ZIP path and number of questions in the session
        request.session['final_zip_path'] = result['zip_path']
        request.session['no_questions'] = result['total_questions']
        response_data['message'] = f"Renamed JSON files in the zip. Total questions: {result['total_questions']}."

    elif step == "upload_s3":
        creds = set_aws_credentials()
        s3_file_url = upload_to_s3(cred=creds, file_path=request.session['final_zip_path'])
        if not s3_file_url:
            response_data({'status': 'error', 'message': 'Failed to upload to S3.'}, status=500)
        request.session['s3_file_url'] = s3_file_url
        response_data['message'] = "Uploaded Zip file to S3."

    elif step == "prepare_json":
        json_data = mcq_practice_prepare_json(
            resource_id=request.session['resource_id'],
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            duration=6000,
            parent_id=request.POST.get('topic_id'),
            total_score=100,
            pass_score=80,
            child_order=int(request.POST.get('child_order')),
            order_type=request.POST.get('order_type'),
            no_questions=request.session['no_questions']
        )
        request.session['json_data'] = json_data
        response_data['message'] = "Prepared JSON data for Spread Sheet."

    elif step == "upload_google_sheet":
        google_sheet_info = upload_to_google_sheets(request.session['json_data'],
                                                    f"{request.POST.get('title')} - {request.session['resource_id']}")
        request.session['spreadsheet_id'] = google_sheet_info['spreadsheet_id']
        response_data['message'] = "Spread Sheet prepared."

    elif step == "load_sheet_request":
        final_json = {
            "spread_sheet_name": request.POST.get('title'),
            "spreadsheet_id": request.session['spreadsheet_id'],
            "data_sets_to_be_loaded": ["ResourcesData", "Units", "Exam"],
            "exam_questions_dir_path_url": request.session['s3_file_url'],
            "is_json_converted": False
        }
        sheet_loading_request_id = submit_sheet_loading_request(final_json)
        request.session['sheet_loading_request_id'] = sheet_loading_request_id
        response_data['message'] = "Sheet Loading request sent."

    elif step == "check_task_status":
        task_status, exception_url = get_task_details(request.session['sheet_loading_request_id'])
        if task_status != "SUCCESS":
            return JsonResponse({'status': 'error', 'message': exception_url}, status=400)
        response_data['message'] = "Sheet loading task completed."

    elif step == "unlock_resource":
        unlock_request_id = submit_unlock_resource(request.session['resource_id'])
        request.session['unlock_request_id'] = unlock_request_id
        response_data['message'] = "Resource unlocked successfully."

    elif step == "save_to_db":
        # Get required details from session for database entry
        user = request.user
        title = request.POST.get('title')
        resource_id = request.session['resource_id']
        topic_id = request.POST.get('topic_id')
        child_order = int(request.POST.get('child_order'))
        spreadsheet_name = f"{title} - {resource_id}"
        spreadsheet_id = request.session['spreadsheet_id']
        sheet_loading_request_id = request.session['sheet_loading_request_id']

        unlock_request_id = request.session.get('unlock_request_id')
        s3_file_url = request.session['s3_file_url']
        processing_duration = time.time() - request.session.get('start_time', time.time())

        # Save to the ResourceLoad model
        ResourceLoadData.objects.create(
            user=user,
            title=title,
            resource_id=resource_id,
            topic_id=topic_id,
            child_order=child_order,
            spreadsheet_name=spreadsheet_name,
            spreadsheet_id=spreadsheet_id,
            sheet_loading_request_id=sheet_loading_request_id,
            unlock_request_id=unlock_request_id,
            no_questions=int(request.session['no_questions']),
            file_url=s3_file_url,
            status="Completed" if unlock_request_id else "Failed",
            resource_type="MCQ PRACTICE",
            updated_count=0,
            processing_duration=processing_duration
        )

        response_data['message'] = "Data saved to the database."
        response_data['complete'] = True  # Indicate process completion

    else:
        response_data({'status': 'error', 'message': 'Invalid step.'}, status=400)

    return JsonResponse(response_data)
