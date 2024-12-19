import json
import re
from utils.Beta.session_util import get_csrf_token, start_session_and_login


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
