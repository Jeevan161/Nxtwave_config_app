import json
import re

from utils.Beta.session_util import start_session_and_login, get_csrf_token


def delete_resource(resource_id):
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
