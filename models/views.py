import shutil
import zipfile

import requests
from django.shortcuts import render

# Create your all_views here.
import re
from bs4 import BeautifulSoup
import time
from bs4 import BeautifulSoup
import os
import uuid

import boto3
from models.views import *
import json
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def set_aws_credentials():
    """Set AWS credentials by logging in and extracting them from the HTML page."""
    session = start_session_and_login()
    if not session:
        print("Failed to start session and login.")
        return None

    url = "https://nkb-backend-ccbp-beta.earlywave.in/admin/nkb_load_data/uploadfile/add/"
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the script tag containing the AWS credentials
    script_tag = soup.find("script", text=re.compile("AWS.Credentials"))
    if not script_tag:
        print("Could not find AWS credentials script.")
        return None

    # Extract AWS credentials using regular expressions
    aws_access_key_id = re.search(r"AWS\.Credentials\(\s*'([^']+)'", script_tag.text)
    aws_secret_access_key = re.search(r"AWS\.Credentials\(\s*'[^']+',\s*'([^']+)'", script_tag.text)
    aws_session_token = re.search(r"AWS\.Credentials\(\s*'[^']+',\s*'[^']+',\s*'([^']+)'", script_tag.text)

    if aws_access_key_id and aws_secret_access_key and aws_session_token:
        credentials = {
            "aws_access_key_id": aws_access_key_id.group(1),
            "aws_secret_access_key": aws_secret_access_key.group(1),
            "aws_session_token": aws_session_token.group(1)
        }
        print("AWS credentials set successfully.")
        return credentials
    else:
        print("Failed to extract AWS credentials.")
        return None

def delete_resource_request(resource_id):
    """Delete a resource using its resource ID."""
    # Start a session and log in
    session = start_session_and_login()

    # URL for deletion form
    form_url = "https://nkb-backend-ccbp-beta.earlywave.in/admin/nkb_load_data/contentloading/add/"
    csrf_token = get_csrf_token(session, form_url)

    # Prepare JSON for resource ID deletion
    input_data = json.dumps({
        "resource_ids": [resource_id],
        "resource_type": "UNIT"
    })

    # Form data for delete request
    form_data = {
        "csrfmiddlewaretoken": csrf_token,
        "task_type": "DELETE_RESOURCES",
        "input_data": input_data,
        "_continue": "Save and view"
    }

    # Set headers and send POST request
    headers = {
        'Referer': form_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }

    response = session.post(form_url, data=form_data, headers=headers, allow_redirects=True)

    # Extract and return request ID from redirect URL
    if response.history:
        final_referer_url = response.url
        match = re.search(r'/contentloading/([a-f0-9\-]+)/change/', final_referer_url)
        if match:
            request_id = match.group(1)
            print(f"Extracted Request ID: {request_id}")
            return request_id  # Successfully extracted request ID

    # Return None if the deletion failed
    print("Failed to submit deletion request.")
    return None



def coding_practice_prepare_json(resource_id, title, duration, parent_id, child_order):
    """
    Prepare JSON data based on the user inputs, formatted for Google Sheets upload.
    """
    common_unit_id = str(uuid.uuid4())

    # Prepare the JSON structure with headers and rows for each section
    json_data = {
        "ResourcesData": {
            "headers": [
                "resource_id", "resource_type", "dependent_resource_count", "dependent_resources",
                "dependent_reason_display_text", "parent_resource_count", "child_order",
                "parent_resources", "auto_unlock"
            ],
            "rows": [
                # First row: Parent resource data
                [
                    resource_id,
                    "UNIT",
                    0,  # dependent_resource_count
                    None,  # dependent_resources
                    None,  # dependent_reason_display_text
                    1,  # parent_resource_count
                    "",  # Empty for parent row
                    "",  # Empty for parent row
                    True  # auto_unlock
                ],
                # Second row: Child resource data
                [
                    "",  # Empty for child row
                    "",  # Empty for child row
                    "",  # Empty for child row
                    "",  # Empty for child row
                    "",  # Empty for child row
                    "",  # Empty for child row
                    child_order,
                    parent_id,
                    ""  # auto_unlock not applicable for child row
                ]
            ]
        },
        "Units": {
            "headers": ["unit_id", "common_unit_id", "unit_type", "duration_in_sec", "tags"],
            "rows": [
                [
                    resource_id,
                    common_unit_id,
                    "QUESTION_SET",
                    duration,
                    "MOCK_TEST_EVALUATION"
                ]
            ]
        },
        "QuestionSet": {
            "headers": ["question_set_id", "title", "content_type"],
            "rows": [
                [
                    resource_id,
                    title,
                    "CODING"
                ]
            ]
        }
    }

    # Print JSON for debugging
    print(json.dumps(json_data, indent=4))

    return json_data



def rename_json_files_in_zip(zip_file, output_dir, uuid):
    """
    Rename all JSON files in the provided ZIP with a specified UUID without changing the structure.
    Returns the path of the modified ZIP file.
    """
    temp_extract_dir = os.path.join(output_dir, 'temp_extract')
    temp_output_dir = os.path.join(output_dir, 'temp_output')

    # Create temporary directories for extraction and output
    os.makedirs(temp_extract_dir, exist_ok=True)
    os.makedirs(temp_output_dir, exist_ok=True)

    # Extract the uploaded zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)

    # Walk through the extracted files, retain structure, and rename JSON files
    for dirpath, _, filenames in os.walk(temp_extract_dir):
        for filename in filenames:
            src_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(src_path, temp_extract_dir)
            dest_path = os.path.join(temp_output_dir, relative_path)

            # Create directories in the output directory (preserving folder structure)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # If it's a JSON file, rename it to {uuid}.json
            if filename.endswith('.json'):
                new_filename = f"{uuid}.json"
                dest_path = os.path.join(os.path.dirname(dest_path), new_filename)

            # Copy the file (renaming JSON files, preserving others)
            shutil.copy(src_path, dest_path)

    # Create the final zip file with renamed JSONs and the original structure
    final_zip_path = os.path.join(output_dir, f"modified_{uuid}.zip")
    with zipfile.ZipFile(final_zip_path, 'w') as new_zip:
        for dirpath, _, filenames in os.walk(temp_output_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                arcname = os.path.relpath(file_path, temp_output_dir)  # Retain folder structure in zip
                new_zip.write(file_path, arcname)

    # Cleanup temporary directories
    shutil.rmtree(temp_extract_dir)
    shutil.rmtree(temp_output_dir)

    return final_zip_path



def start_session_and_login():
    """Start a session and login to the system."""
    session = requests.Session()
    login_url = "https://nkb-backend-ccbp-beta.earlywave.in/admin/login/"

    # Get CSRF token from login page
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

    # Login credentials and CSRF token
    login_data = {
        'username': 'content_loader',
        'password': 'content_loader@432',
        'csrfmiddlewaretoken': csrf_token
    }

    headers = {
        'Referer': login_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.89 Safari/537.36'
    }

    # Log in to the session
    response = session.post(login_url, data=login_data, headers=headers)

    if "Log out" in response.text or response.url != login_url:
        print("Login successful.")
        return session
    else:
        print("Login failed.")
        print("Response Text:", response.text[:500])  # Print part of the response for debugging
        return None


def get_csrf_token(session, url):
    """Get the CSRF token from a specified URL."""
    page = session.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
    return csrf_token



def submit_sheet_loading_request(final_json):
    """
    Send a request to initiate sheet loading using the provided spreadsheet name and S3 file URL.

    Args:
        spreadsheet_name (str): The name of the spreadsheet to load data into.
        s3_file_url (str): The URL of the file in S3 containing the data.

    Returns:
        str: The requested ID from the redirect URL if successful, or None if failed.
    """
    session = start_session_and_login()
    if not session:
        print("Session could not be established. Login failed.")
        return None

    form_url = "https://nkb-backend-ccbp-beta.earlywave.in/admin/nkb_load_data/contentloading/add/"
    csrf_token = get_csrf_token(session, form_url)

    # Construct the final JSON payload for the request


    # Prepare the form data
    form_data = {
        "csrfmiddlewaretoken": csrf_token,
        "task_type": "SHEET_LOADING",
        "input_data": json.dumps(final_json),
        "_continue": "Save and view"
    }

    headers = {
        'Referer': form_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }

    response = session.post(form_url, data=form_data, headers=headers, allow_redirects=True)

    # Extract the requested ID from the final redirect URL, if available
    if response.history:
        final_referer_url = response.url
        match = re.search(r'/contentloading/([a-f0-9\-]+)/change/', final_referer_url)
        if match:
            requested_id = match.group(1)
            print(f"Extracted Requested ID: {requested_id}")
            return requested_id

    print("Failed to extract the requested ID.")
    return None



GOOGLE_SHEET_CREDENTIALS = {
    "type": "service_account",
    "project_id": "corded-pivot-429113-g1",
    "private_key_id": "4e9d7f0ed8b4ee6e34c5035a30c63eb7c0362f4c",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDR75dROrzRJ2Tc\n0jA6vBwyHqP1AZwLQ5lmViWbNzPmSknePYCjSxAPLOlogwXOgkiR/TuNUVUe+T7a\n9A5dEcYi/dACZZ406lYM22i0+2Q9oyDYXqTzjdtLI3cGLMXRE1CwKSKIstg6YbZq\n/IKiKsuw5kgcpS8y/Y3kqHC/Fmt9ycf6MDytDc2KUXZHYFI3rURo64P9MoNq2CyJ\nkmnHGc88wohTd6IEZ98MzBHe6wgslnkqQQdtiyn8jfHmKhxBwJG3ahQ5KdSR9H+J\ng7mlak/D3L2a0pzul/g2iDOh9EvbZ5OF/dZRR5htUgqiGykBA4DHBss87BxmrQIJ\n3lVAkKxPAgMBAAECggEAaMQh5gojh1ca+S41nmIYyhRLay4R8vcZux3bp5GNZ2wE\nYBGePB9uFLyrgJn+UFfpIl3XFceUbKAi836fGmgP0o+Kel++65ZUOhdWshbQqAfc\nEM5ukBLncKByuhSm5Zc3iaoFj2V9DemMcOixwn8L5qyNKSpwGwi5AnbiySHFo+Ai\nT2VM6dvWQBCzNR91gBAQNkbxFqu+kygAHetVdf0ClOOi52WoiAnDHjXbn9Ollco7\nv1l21CAtY/OJoHR1PhNjEq5L019kuO+KPdGAJ3AMxlNGhKvXE48nDgifjalCsgZM\nI+HiyykdfHxRec1FsB0FEzxbGAiF58pMO7XoLLpsrQKBgQD58kksMluBw97aBpxn\nHhdDk9V83bQbOAc4f8K4OTU+pZII2VykidZKH2is8JGJXvKyD8JlV2CwLGlfsELv\n+S7neNcVg6tU4gE6CJniFMl7q1UGDecWRY3/ZqW+7F+xXPH+leWMY5cstqGHcdIf\nt41yxsSjgml0pwcKkcRSJ85MYwKBgQDXBTuKG8RxawYRtXiSEBE6c4oXEA0zbj/S\noKhyoYY1YNqH6iiUQcxGRgm6esCCR3af+znxMJxgZXmhlm0iTKBjIrenmJ72WTtn\nXrurEwcXmr4ydwsgmGdkMvJ4WsqlKxnk1r/cZh1non8LHGnWUs4zqiM9+Zg5ZyRY\nIUhW8m52JQKBgFjglrRok7Fo/O16PFNOl+cnwlpMW6byHV8xzwPDE/Pa3DrZT+AS\nQ2jIEmisgpPed15pzC5NC8yZfj7QZnz+lncouRKlZ18fnmAMfuutiJe5LNqiRvHc\necm/rmBdnQlsi4CDvMRXBYKYzodjKdytYFbX50RdMzKP0ikn/C9aiDkRAoGBAM/L\nv8F1mj/dpQziKnZFztCFLjOhkJBegJFmL8QwM0pMooRtF/BHMknLj8VGsdp1g7+S\nA2oCh21lQ8mUXT2jffCwcXonNaBvlcgNNiJbDiSSqDKO9xL2Fh0wW0FSxLogUDLm\nEp7FlK89y7cKK4IznhEx4EMZfjIjam09JPLZ8UR9AoGAVSHXdf2ieG7xc1XYxBl1\n8voXu8+5QdoOAZeboEC7tzK+iuUoFCX6zlyGV9YrT0tcbbB1a4RQixcXROe1uQJ/\n2aSvpcKjLuzEmGQ86q+cAtXQjGmx8LieUAWI23dLds42nnEkUwKh9/8mKoYdxp+p\nc3OJ/lkd1vnzMVBAmA9lkn8=\n-----END PRIVATE KEY-----\n",
    "client_email": "tutorial-configuration-script@corded-pivot-429113-g1.iam.gserviceaccount.com",
    "client_id": "111171826741023448042",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tutorial-configuration-script%40corded-pivot-429113-g1.iam.gserviceaccount.com",
}


def authorize_google_sheets():
    """Authorize Google Sheets API using service account credentials."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEET_CREDENTIALS, scope)
    return gspread.authorize(creds)


def upload_to_google_sheets(json_data, sheet_name):
    """
    Upload JSON data to Google Sheets, create separate sheets for each JSON section,
    and share the spreadsheet with specified user emails.

    Args:
        json_data (dict): The JSON data with headers and rows for each section.
        sheet_name (str): The name for the Google Spreadsheet.
        user_emails (list, optional): List of emails to share the sheet with.

    Returns:
        str: URL of the created Google Spreadsheet.
    """
    client = authorize_google_sheets()
    spreadsheet = client.create(sheet_name)

    # Set default editor permissions for each user in user_emails if provided
    spreadsheet.share('learningresource@nkblearningbackend.iam.gserviceaccount.com', perm_type='user', role='writer')
    spreadsheet.share('jeevansravanth.parisa@nxtwave.co.in', perm_type='user', role='writer')

    # Create individual sheets for each JSON section and add data
    for key, data in json_data.items():
        worksheet = spreadsheet.add_worksheet(title=key, rows="100", cols="20")

        # Add headers if they exist in the data
        if 'headers' in data:
            worksheet.append_row(data['headers'])

        # Add rows of data
        for row in data.get('rows', []):
            worksheet.append_row(row)

    return {
        "url": spreadsheet.url,
        "title": spreadsheet.title,
        "spreadsheet_id": spreadsheet.id
    }




def get_task_details(request_id, check_interval=4):
    """
    Fetch task details based on the request ID and keep checking until status is 'SUCCESS' or 'FAILED'.

    Args:
        request_id (str): The ID of the request to check.
        check_interval (int): Interval in seconds to wait between checks.

    Returns:
        tuple: task_status (str), exception (str) - "FAILURE" or "SUCCESS" and exception URL or empty string.
    """
    session = start_session_and_login()
    url = f"https://nkb-backend-ccbp-beta.earlywave.in/admin/nkb_load_data/contentloading/{request_id}/change/"

    while True:
        response = session.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract Task Output URL
            task_output_div = soup.find('div', class_='form-row field-task_output_url')
            task_output_url = task_output_div.find('div',
                                                   class_='readonly').text.strip() if task_output_div else ""

            # Extract Task Status
            task_status_div = soup.find('div', class_='form-row field-task_status')
            task_status = task_status_div.find('div',
                                               class_='readonly').text.strip() if task_status_div else "No Task Status found"

            # Check if task is no longer in progress
            if task_status not in ["IN_PROGRESS"]:
                break

        # Wait before checking again
        time.sleep(check_interval)

    # Default exception message
    exception = ""

    if task_status == "FAILED":
        try:
            # Parse task_output_url as JSON
            task_output_data = json.loads(task_output_url)
            exception = task_output_data.get("exception", "")
        except json.JSONDecodeError:
            exception = "Error parsing task output."

    return task_status, exception



def submit_unlock_resource(request_id):
    """
    Unlock resources for users using the provided request ID.

    Args:
        request_id (str): The ID of the resource to unlock.

    Returns:
        str: The requested ID if the unlock request is successful, or None if it fails.
    """
    # Start session and login
    session = start_session_and_login()
    if not session:
        print("Failed to start a session.")
        return None

    # Define URL and CSRF token
    form_url = "https://nkb-backend-ccbp-beta.earlywave.in/admin/nkb_load_data/contentloading/add/"
    csrf_token = get_csrf_token(session, form_url)

    # Create the request payload
    input_data = {
        "resource_ids": [request_id]
    }

    form_data = {
        "csrfmiddlewaretoken": csrf_token,
        "task_type": "UNLOCK_RESOURCES_FOR_USERS",
        "input_data": json.dumps(input_data),
        "_continue": "Save and view"
    }

    headers = {
        'Referer': form_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }

    # Send the POST request
    response = session.post(form_url, data=form_data, headers=headers, allow_redirects=True)

    # Check if there was a redirect indicating success
    if response.history:
        final_referer_url = response.url
        match = re.search(r'/contentloading/([a-f0-9\-]+)/change/', final_referer_url)
        if match:
            requested_id = match.group(1)
            print(f"Unlock request completed successfully. Extracted Requested ID: {requested_id}")
            return requested_id

    # If no redirect or an error occurred, return None
    print("Failed to complete the unlock request.")
    return None


S3_BUCKET_NAME = 'nkb-backend-ccbp-media-static'
S3_REGION_NAME = 'ap-south-1'
S3_UPLOAD_FOLDER = 'ccbp_beta/media/content_loading/uploads/'


def upload_to_s3(cred, file_path):
    """Upload a file to S3 using the provided credentials."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=cred['aws_access_key_id'],
        aws_secret_access_key=cred['aws_secret_access_key'],
        aws_session_token=cred['aws_session_token'],
        region_name='ap-south-1'
    )

    # Generate a unique file name using UUID
    file_name = os.path.basename(file_path)
    unique_file_name = f"{uuid.uuid4()}_{file_name}"
    s3_key = f"{S3_UPLOAD_FOLDER}{unique_file_name}"

    try:
        print(f"Uploading file {file_path} to S3 bucket at {s3_key}")
        s3_client.upload_file(file_path, 'nkb-backend-ccbp-media-static', s3_key, ExtraArgs={'ACL': 'public-read'})
        s3_file_url = f"https://nkb-backend-ccbp-media-static.s3.ap-south-1.amazonaws.com/{s3_key}"
        print(f"File uploaded successfully to: {s3_file_url}")
        return s3_file_url
    except Exception as e:
        print(f"Failed to upload to S3: {e}")
        return None
