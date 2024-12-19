# views.py

import time
import uuid
import zipfile
from io import BytesIO
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from models.models import ResourceLoadData
from utils.Beta.sheet_loading import submit_sheet_loading_request
from utils.Beta.tt_gsheet import upload_to_google_sheets_single_sheet
from utils.Beta.unlock_resource import submit_unlock_resource
from utils.Beta.task_details import get_task_details


# Initialize


@login_required
def zip_tutorial_view(request):
    """
    Renders the tutorial creation page for uploading ZIP files.
    """
    if request.method == 'GET':
        return render(request, 'Beta/zip_tutorial.html')


@login_required
@csrf_exempt  # **Security Note:** It's recommended to remove this in production and handle CSRF properly.
def zip_tutorial_process(request):
    """
    Processes each step of tutorial creation asynchronously based on the `step` parameter from the request.
    Handles multiple Markdown files contained within a ZIP archive.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

    step = request.POST.get('step')
    response_data = {'status': 'success', 'step': step, 'message': ''}

    try:
        if step == "initialize":
            # Initialize the process by setting up session variables
            request.session['start_time'] = time.time()
            response_data['message'] = "Tutorial process initialized."


        elif step == "process_markdown":
            # Process the uploaded ZIP file containing markdown files
            zip_file = request.FILES.get('zip_file')
            if not zip_file:
                return JsonResponse({"status": "error", "message": "ZIP file is missing."}, status=400)

            # Validate ZIP file
            if not zipfile.is_zipfile(zip_file):
                return JsonResponse({"status": "error", "message": "Uploaded file is not a valid ZIP archive."},
                                    status=400)

            # Log the size of the uploaded file

            # Read and extract markdown files from the ZIP archive
            md_files = []
            try:
                # Reset the file pointer to the beginning
                zip_file.seek(0)
                with zipfile.ZipFile(zip_file) as z:
                    for file_info in z.infolist():
                        if file_info.filename.endswith('.md'):
                            with z.open(file_info) as md_file:
                                try:
                                    content = md_file.read().decode('utf-8')
                                except UnicodeDecodeError:

                                    return JsonResponse({"status": "error",
                                                         "message": f"File {file_info.filename} is not a valid UTF-8 encoded Markdown file."},
                                                        status=400)
                                file_name = file_info.filename
                                md_files.append({'name': file_name, 'content': content})

            except zipfile.BadZipFile as e:

                return JsonResponse({"status": "error", "message": "Bad ZIP file."}, status=400)
            except Exception as e:

                return JsonResponse({"status": "error",
                                     "message": f"An unexpected error occurred while processing the ZIP file: {str(e)}"},
                                    status=500)

            if not md_files:
                return JsonResponse({"status": "error", "message": "No markdown files found in the ZIP archive."},
                                    status=400)

            # Retrieve additional parameters
            topic_id = request.POST.get("topic_id")
            if not topic_id:
                return JsonResponse({"status": "error", "message": "Topic ID is missing."}, status=400)

            try:
                child_order_start = int(request.POST.get("child_order", 0))
            except ValueError:

                return JsonResponse({"status": "error", "message": "Child Order must be an integer."}, status=400)

            # Process each markdown file
            tutorials_json = []
            for index, md_file in enumerate(md_files):
                resource_id = str(uuid.uuid4())
                learning_rs_id = str(uuid.uuid4())
                # Handle cases where the ZIP may contain directories
                title = md_file['name'].rsplit('/', 1)[-1].rsplit('.', 1)[
                    0]  # Remove directory path and .md extension for the title
                tutorial_json = process_single_markdown(md_file['name'], md_file['content'], learning_rs_id)
                tutorials_json.append({
                    'resource_id': resource_id,
                    'learning_rs_id': learning_rs_id,
                    'tutorial_json': tutorial_json,
                    'title': title
                })

            # Store the processed data in the session
            request.session['tutorials_data'] = tutorials_json
            request.session['topic_id'] = topic_id
            request.session['child_order_start'] = child_order_start
            response_data['message'] = f"{len(tutorials_json)} Markdown files processed."


        elif step == "prepare_additional_json":
            # Add additional JSON data required for Google Sheets
            topic_id = request.session.get('topic_id')
            child_order_start = request.session.get('child_order_start', 0)

            tutorials_data = request.session.get('tutorials_data')
            if not tutorials_data:
                return JsonResponse({"status": "error", "message": "Tutorials data is missing."}, status=400)

            # Prepare combined JSON structures
            resources_data_rows = []
            units_rows = []
            learning_resource_set_rows = []
            learning_resources_rows = []

            child_order = child_order_start
            for tutorial in tutorials_data:
                resource_id = tutorial['resource_id']
                learning_rs_id = tutorial['learning_rs_id']
                title = tutorial['title']

                # ResourcesData rows
                resources_data_rows.append([
                    resource_id, "UNIT", 0, "", "", 1, "", "", ""
                ])
                resources_data_rows.append([
                    "", "", "", "", "", "", child_order, topic_id, ""
                ])

                # Units rows
                units_rows.append([
                    resource_id, str(uuid.uuid4()), "LEARNING_SET", 1500, "CHEAT_SHEET"
                ])

                # LearningResourceSet rows
                learning_resource_set_rows.append([
                    resource_id, title, 1, "", "", "TUTORIAL"
                ])
                learning_resource_set_rows.append([
                    "", "", "", learning_rs_id, 1, ""
                ])

                # LearningResources rows
                learning_resources_rows.append([
                    learning_rs_id, title, "", "MARKDOWN", "ENGLISH", 0, "", 600, "", "",
                    0, 600, "", title, "DEFAULT"
                ])

                # Increment child_order for the next tutorial
                child_order += 1

            additional_json = {
                "ResourcesData": {
                    "headers": [
                        "resource_id", "resource_type", "dependent_resource_count", "dependent_resources",
                        "dependent_reason_display_text", "parent_resource_count", "child_order",
                        "parent_resources", "auto_unlock"
                    ],
                    "rows": resources_data_rows
                },
                "Units": {
                    "headers": ["unit_id", "common_unit_id", "unit_type", "duration_in_sec", "tags"],
                    "rows": units_rows
                },
                "LearningResourceSet": {
                    "headers": [
                        "learning_resource_set_id", "learning_resource_set_name",
                        "learning_resources_count", "learning_resource_ids", "order", "learning_resource_set_type"
                    ],
                    "rows": learning_resource_set_rows
                },
                "LearningResources": {
                    "headers": [
                        "learning_resource_id", "Title", "Content", "content_format", "content_language",
                        "multimedia_count", "multimedia_format", "total_duration", "multimedia_url", "thumbnail_url",
                        "highlights_count", "duration_in_sec", "content", "title", "learning_resource_type"
                    ],
                    "rows": learning_resources_rows
                }
            }

            request.session['additional_json'] = additional_json
            response_data['message'] = "Additional JSON data prepared."


        elif step == "upload_google_sheet":
            # Upload data to Google Sheets
            tutorials_data = request.session.get('tutorials_data')
            additional_json = request.session.get('additional_json')
            if not tutorials_data or not additional_json:
                return JsonResponse({"status": "error", "message": "JSON data is missing."}, status=400)

            # Generate a unique title for the spreadsheet
            title = f"Tutorials Batch - {time.strftime('%Y%m%d-%H%M%S')}"

            # Combine all tutorial JSON data
            combined_tutorial_json = {
                "Tutorial": {
                    "headers": ["tutorial_id", "entity_id", "entity_type"],
                    "rows": []
                },
                "TutorialStep": {
                    "headers": ["tutorial_step_id", "tutorial_id", "step_entity_id", "step_entity_type", "order",
                                "content", "content_format"],
                    "rows": []
                }
            }

            for tutorial in tutorials_data:
                tutorial_json = tutorial['tutorial_json']
                combined_tutorial_json["Tutorial"]["rows"].extend(tutorial_json["Tutorial"]["rows"])
                combined_tutorial_json["TutorialStep"]["rows"].extend(tutorial_json["TutorialStep"]["rows"])

            # Merge combined_tutorial_json with additional_json
            combined_json = {**additional_json, **combined_tutorial_json}

            # Upload to Google Sheets
            spreadsheet_id = upload_to_google_sheets_single_sheet(combined_json, {}, title, request.user.email)
            request.session['spreadsheet_id'] = spreadsheet_id
            response_data['message'] = "Data uploaded to Google Sheets."


        elif step == "submit_sheet_loading_request":
            # Submit sheet loading request
            topic_id = request.session.get('topic_id')
            spreadsheet_id = request.session.get('spreadsheet_id')
            if not topic_id or not spreadsheet_id:
                return JsonResponse({"status": "error", "message": "Topic ID or Spreadsheet ID is missing."},
                                    status=400)

            sheet_loading_request_id = submit_sheet_loading_request({
                "spread_sheet_name": topic_id,  # Assuming the sheet name is based on topic_id
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
            # Unlock all resources
            tutorials_data = request.session.get('tutorials_data')
            if not tutorials_data:
                return JsonResponse({"status": "error", "message": "Tutorials data is missing."}, status=400)

            unlock_request_ids = []
            for tutorial in tutorials_data:
                resource_id = tutorial['resource_id']
                unlock_request_id = submit_unlock_resource(resource_id)
                unlock_request_ids.append(unlock_request_id)

            request.session['unlock_request_ids'] = unlock_request_ids
            response_data['message'] = "Resources unlocked successfully."


        elif step == "save_to_db":
            # Save all data to the database
            user = request.user
            topic_id = request.session.get('topic_id')
            child_order_start = request.session.get('child_order_start', 0)
            spreadsheet_id = request.session.get('spreadsheet_id')
            sheet_loading_request_id = request.session.get('sheet_loading_request_id')
            unlock_request_ids = request.session.get('unlock_request_ids')
            processing_duration = time.time() - request.session.get('start_time', time.time())
            tutorials_data = request.session.get('tutorials_data')

            if not all([topic_id, spreadsheet_id, sheet_loading_request_id, tutorials_data]):
                return JsonResponse({"status": "error", "message": "Missing required session data."}, status=400)

            status = "Completed" if unlock_request_ids else "Failed"
            child_order = child_order_start

            # Save each tutorial separately in the database
            for tutorial in tutorials_data:
                ResourceLoadData.objects.create(
                    user=user,
                    title=tutorial['title'],
                    resource_id=tutorial['resource_id'],
                    topic_id=topic_id,
                    child_order=child_order,
                    spreadsheet_name=f"{tutorial['title']} - {tutorial['resource_id']}",
                    spreadsheet_id=spreadsheet_id,
                    file_url="",  # No file URL as content is processed directly
                    status=status,
                    resource_type="TUTORIAL",
                    updated_count=0,
                    processing_duration=processing_duration
                )

                child_order += 1

            response_data['message'] = "Tutorial data saved to the database."
            response_data['complete'] = True  # Indicate the entire process is complete


        else:

            return JsonResponse({"status": "error", "message": "Invalid step."}, status=400)

    except Exception as e:
        # Log the exception with traceback

        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse(response_data)


def process_single_markdown(file_name, content, learning_rs_id):
    """
    Processes a single markdown file's content and generates JSON data for Tutorial and TutorialSteps.

    Args:
        file_name (str): The name of the markdown file.
        content (str): The markdown content to process.
        learning_rs_id (str): The learning resource set ID.

    Returns:
        dict: A JSON structure containing 'Tutorial' and 'TutorialStep' keys in a consistent format.
    """
    # Split content into parts using a custom delimiter
    content_parts = split_content_by_delimiter(content)

    # Generate the tutorial JSON
    tutorial_id = str(uuid.uuid4())  # Generate a unique tutorial ID

    # Convert the Tutorial to headers and rows
    tutorial_data = {
        "headers": ["tutorial_id", "entity_id", "entity_type"],
        "rows": [[tutorial_id, learning_rs_id, "LEARNING_RESOURCE"]]
    }

    # Convert the TutorialStep to headers and rows
    tutorial_steps_data = {
        "headers": ["tutorial_step_id", "tutorial_id", "step_entity_id", "step_entity_type", "order", "content",
                    "content_format"],
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
