import time
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from models.models import ResourceLoadData
from utils.Beta.sheet_loading import submit_sheet_loading_request
from utils.Beta.tt_gsheet import upload_to_google_sheets_single_sheet
from utils.Beta.unlock_resource import submit_unlock_resource
from utils.Beta.task_details import get_task_details  # Ensure this is imported


@login_required
def tutorial_view(request):
    if request.method == 'GET':

        return render(request, 'Beta/tutorial.html')


@login_required
@csrf_exempt
def tutorial_process(request):
    """
    Processes each step of tutorial creation asynchronously based on the `step` parameter from the request.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

    step = request.POST.get('step')
    response_data = {'status': 'success', 'step': step, 'message': ''}
    print(f"Processing step: {step}")

    try:
        if step == "initialize":
            # Initialize the process by setting up session variables
            request.session['resource_id'] = str(uuid.uuid4())
            request.session['common_rs_id'] = str(uuid.uuid4())
            request.session['learning_rs_id'] = str(uuid.uuid4())
            request.session['start_time'] = time.time()
            response_data['message'] = "Tutorial process initialized."

        elif step == "process_markdown":
            # Process the uploaded markdown file
            md_file = request.FILES.get('md_file')
            if not md_file:
                return JsonResponse({"status": "error", "message": "Markdown file is missing."}, status=400)

            content = md_file.read().decode("utf-8")
            file_name = md_file.name
            resource_id = request.session['resource_id']
            learning_rs_id = request.session['learning_rs_id']
            tutorial_json = process_single_markdown(file_name, content, learning_rs_id)
            request.session['tutorial_json'] = tutorial_json
            response_data['message'] = "Markdown content processed."

        elif step == "prepare_additional_json":
            # Add additional JSON data required for Google Sheets
            title = request.POST.get("title")
            topic_id = request.POST.get("topic_id")
            child_order = int(request.POST.get("child_order", 0))

            if not title or not topic_id:
                return JsonResponse({"status": "error", "message": "Title or Topic ID is missing."}, status=400)

            # Store required fields in session for later use
            request.session['title'] = title
            request.session['topic_id'] = topic_id
            request.session['child_order'] = child_order

            additional_json = {
                "ResourcesData": {
                    "headers": [
                        "resource_id", "resource_type", "dependent_resource_count", "dependent_resources",
                        "dependent_reason_display_text", "parent_resource_count", "child_order",
                        "parent_resources", "auto_unlock"
                    ],
                    "rows": [
                        [request.session['resource_id'], "UNIT", 0, "", "", 1, "", "", ""],
                        ["", "", "", "", "", "", child_order, topic_id, ""]
                    ]
                },
                "Units": {
                    "headers": ["unit_id", "common_unit_id", "unit_type", "duration_in_sec", "tags"],
                    "rows": [[request.session['resource_id'], request.session['common_rs_id'], "LEARNING_SET", 1500,
                              "CHEAT_SHEET"]]
                },
                "LearningResourceSet": {
                    "headers": [
                        "learning_resource_set_id", "learning_resource_set_name",
                        "learning_resources_count", "learning_resource_ids", "order", "learning_resource_set_type"
                    ],
                    "rows": [
                        [request.session['resource_id'], title, 1, "", "", "TUTORIAL"],
                        ["", "", "", request.session['learning_rs_id'], 1, ""]
                    ]
                },
                "LearningResources": {
                    "headers": [
                        "learning_resource_id", "Title", "Content", "content_format", "content_language",
                        "multimedia_count", "multimedia_format", "total_duration", "multimedia_url", "thumbnail_url",
                        "highlights_count", "duration_in_sec", "content", "title", "learning_resource_type"
                    ],
                    "rows": [
                        [
                            request.session['learning_rs_id'], title, "", "MARKDOWN", "ENGLISH", 0, "", 600, "", "",
                            0, 600, "", title, "DEFAULT"
                        ]
                    ]
                }
            }
            request.session['additional_json'] = additional_json
            response_data['message'] = "Additional JSON data prepared."

        elif step == "upload_google_sheet":
            # Upload data to Google Sheets
            tutorial_json = request.session.get('tutorial_json')
            additional_json = request.session.get('additional_json')
            title = request.session.get('title')

            if not tutorial_json or not additional_json or not title:
                return JsonResponse({"status": "error", "message": "JSON data or title is missing."}, status=400)

            spreadsheet_id = upload_to_google_sheets_single_sheet(tutorial_json, additional_json, title,request.user.email)
            request.session['spreadsheet_id'] = spreadsheet_id
            response_data['message'] = "Data uploaded to Google Sheets."

        elif step == "submit_sheet_loading_request":
            # Submit sheet loading request
            title = request.session.get('title')
            spreadsheet_id = request.session.get('spreadsheet_id')
            sheet_loading_request_id = submit_sheet_loading_request({
                "spread_sheet_name": title,
                "spreadsheet_id": spreadsheet_id,
                "data_sets_to_be_loaded": ["ResourcesData", "Units", "LearningResourceSet", "LearningResources",
                                           "Tutorial", "TutorialStep"]
            })
            request.session['sheet_loading_request_id'] = sheet_loading_request_id
            response_data['message'] = "Sheet loading request submitted."

        elif step == "check_task_status":
            # Check the status of the sheet loading task
            sheet_loading_request_id = request.session.get('sheet_loading_request_id')
            if not sheet_loading_request_id:
                return JsonResponse({"status": "error", "message": "Sheet loading request ID is missing."}, status=400)

            task_status, exception_url = get_task_details(sheet_loading_request_id)
            if task_status != "SUCCESS":
                return JsonResponse({"status": "error", "message": "Sheet loading task failed."}, status=500)
            response_data['message'] = "Sheet loading task completed successfully."

        elif step == "unlock_resource":
            # Unlock the resource
            resource_id = request.session['resource_id']
            unlock_request_id = submit_unlock_resource(resource_id)
            request.session['unlock_request_id'] = unlock_request_id
            response_data['message'] = "Resource unlocked successfully."

        elif step == "save_to_db":
            # Save all data to the database
            user = request.user
            title = request.session.get('title')
            topic_id = request.session.get('topic_id')
            child_order = request.session.get('child_order')
            spreadsheet_id = request.session.get('spreadsheet_id')
            sheet_loading_request_id = request.session.get('sheet_loading_request_id')
            unlock_request_id = request.session.get('unlock_request_id')
            processing_duration = time.time() - request.session.get('start_time', time.time())
            resource_id = request.session.get('resource_id')

            if not all([title, topic_id, child_order, spreadsheet_id, sheet_loading_request_id]):
                return JsonResponse({"status": "error", "message": "Missing required session data."}, status=400)

            ResourceLoadData.objects.create(
                user=user,
                title=title,
                resource_id=resource_id,
                topic_id=topic_id,
                child_order=child_order,
                spreadsheet_name=f"{title} - {resource_id}",
                spreadsheet_id=spreadsheet_id,
                file_url="",  # No file URL as content is processed directly
                status="Completed" if unlock_request_id else "Failed",
                resource_type="TUTORIAL",
                updated_count=0,
                processing_duration=processing_duration
            )

            response_data['message'] = "Tutorial data saved to the database."
            response_data['complete'] = True  # Indicate the entire process is complete

        else:
            return JsonResponse({"status": "error", "message": "Invalid step."}, status=400)

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse(response_data)


def process_single_markdown(file_name, content,learning_rs_id):
    """
    Processes a single markdown file's content and generates JSON data for Tutorial and TutorialSteps.

    Args:
        file_name (str): The name of the markdown file.
        content (str): The markdown content to process.

    Returns:
        dict: A JSON structure containing 'Tutorial' and 'TutorialStep' keys in a consistent format.
    """
    # Split content into parts using a custom delimiter
    content_parts = split_content_by_delimiter(content)

    # Generate the tutorial JSON
    cheat_sheet_id = learning_rs_id  # Extract CheatSheetID from file name
    tutorial_id = str(uuid.uuid4())  # Generate a unique tutorial ID

    # Convert the Tutorial to headers and rows
    tutorial_data = {
        "headers": ["tutorial_id", "entity_id", "entity_type"],
        "rows": [[tutorial_id, cheat_sheet_id, "LEARNING_RESOURCE"]]
    }

    # Convert the TutorialStep to headers and rows
    tutorial_steps_data = {
        "headers": ["tutorial_step_id", "tutorial_id", "step_entity_id", "step_entity_type", "order", "content", "content_format"],
        "rows": [
            [
                str(uuid.uuid4()), tutorial_id, "", "", index + 1, part.strip(), "MARKDOWN"
            ]
            for index, part in enumerate(content_parts)
        ]
    }

    return {
        "Tutorial": tutorial_data,
        "TutorialStep": tutorial_steps_data
    }



def split_content_by_delimiter(content, delimiter="++==PART++=="):
    """
    Splits markdown content into parts using a custom delimiter.

    Args:
        content (str): The markdown content to split.
        delimiter (str): The delimiter to use for splitting. Default is "++==PART++==".

    Returns:
        list: A list of content parts split by the delimiter.
    """
    return content.split(delimiter)
