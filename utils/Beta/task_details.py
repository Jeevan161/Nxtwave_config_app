import json
import time
import requests
from bs4 import BeautifulSoup
from utils.Beta.session_util import start_session_and_login

def get_task_details(request_id, check_interval=4):
    session = start_session_and_login()
    url = f"https://nkb-backend-ccbp-beta.earlywave.in/admin/nkb_load_data/contentloading/{request_id}/change/"

    while True:
        response = session.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract Task Output URL - Adjust based on actual HTML content
            task_output_div = soup.find('div', class_='form-row field-task_output_url')
            # print(task_output_div)
            if task_output_div:
                task_output_text = task_output_div.find('div', class_='readonly').get_text(strip=True)
                # print(task_output_text)
                try:
                    # The text is treated as a JSON string; parsing the JSON to get details
                    task_output_data = json.loads(task_output_text)
                    output_url = task_output_data.get("output")
                    exception = task_output_data.get("exception")
                    response = task_output_data.get("response")
                    sheet_loading_status = task_output_data.get("sheet_loading_status")

                    # print(output_url)
                    # Check task status
                    if sheet_loading_status == 'SUCCESS':
                        return "SUCCESS", ""

                    if response and "status" in response and response["status"] == "SUCCESS":
                        return "SUCCESS", ""
                    if output_url:
                        if exception == "":
                            print("SUCCESS")
                            return "SUCCESS", ""
                    # Handle other statuses or exceptions
                    if exception:
                        return "FAILURE", exception

                except json.JSONDecodeError:
                    print("task_output_url Not found!")

        # Wait before checking again
        time.sleep(check_interval)

    # Default return if loop exits without successful status
    return "INCOMPLETE", "Task status check incomplete or failed"
