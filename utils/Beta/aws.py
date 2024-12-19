import re
from bs4 import BeautifulSoup

from utils.Beta.session_util import start_session_and_login


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
