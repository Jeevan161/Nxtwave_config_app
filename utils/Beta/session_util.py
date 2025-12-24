import requests
from bs4 import BeautifulSoup
import re


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
        'username': 'vishal.yadav',
        'password': 'z2VNwPj14z',
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
