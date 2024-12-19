import json
import re
from utils.Beta.session_util import start_session_and_login, get_csrf_token


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
