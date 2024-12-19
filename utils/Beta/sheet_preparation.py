import gspread
from oauth2client.service_account import ServiceAccountCredentials


GOOGLE_SHEET_CREDENTIALS = {
  "type": "service_account",
  "project_id": "spread-sheet-444418",
  "private_key_id": "50bd5ae6a24640ce06947e41092188a903d7d8e2",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDDfW3JFagIjNrw\nECb33NzAywksAcOhPQrpmLsujwCTscaqKpgPBbENeSqTtzLHJnoxBHon0XI/abPk\nv8Qe50JpCq26tqeg6t9TKLw8kUw/KmDqLLSz2kz7GklbQJkGEiHUnYaBlIXUl4v1\njQfMyK3arMLU8xi/NnRRJpjfzWVwRr6V8/gYO8+iJJK4/Xz0iZSZmLfCBkb0PEzW\n7pgxWX2UPmpr9huhurWSKHZwVzmkOD+Q8SCzOtrf3NP+j6djqz60Q28eiW/TVqrK\n9SUmZ6NuXq+0OWSLEMpU9BR9IvP9WRTYNKSe0y5KhqPJ2oRwn7pVr5txf1f4sQuX\n//ScW+ArAgMBAAECggEAFeMRqx1XGln220DbtA2Q068HwFsUNZW5hozYjC5rkJ2r\nUfsB2lC3UXxa5X3x2/U1Yg6PxKyA/5OMlhRYV2Np/ou5BroTi4MwbMWXSaq04C+U\n+TL3KlnLG6QGSYaye0kFa6IVYKWp1DMBcwUOtgFT4bNM/v2WrDXjEQDixc/fxxGa\nT9X+zMVCzCvLI7KJz/hzppEQWl9hEEK65eSyNuM8U7xo2IKbxYSbjeNM2CZiODJN\nzr2/m3HDb82MHnjDAn7tWVhoOrcKK9ILYLd5fwUkTxaOQ77PtoDAzZ91w2I1929Z\nlTIHnyqhNzIjgz5qTyYeYejQS0IJahOEvrXi4o0RIQKBgQD1QKTC2/3LbEs1grUs\na0c+dNJk5ahLStd46ovaU1hrSLDV0YJlwLEEP9haq6SALXxl8ehqewzRFZqFZZHI\n5BYHjX5jlD9ZAin4OVYfd8vSdlcdaOhlrBLnzq3zQIOfNhX83Zrl5hXncHH13gLt\noY9+oT5Be2pBNYWLHM2K9pyi4QKBgQDMDoabfIqCQA0PJcqFYCr02rKCZk+pygXE\nOAowXvBwcd7jFuvKHERAdHUH2SuRaHsPgZFuQOySmyRArReQ02yKOxD6nVjVdPjh\nSzy7UNbEhdd7U5mVi/3Jdf0ps/HQiv9NnpxwF4HdTOyDug7DvnVpN4hItL2dkhDM\n5e+hnK1wiwKBgQCqptp+hFkqzSXgDB1I1TTzrpIfhvX9vgwEpR+/QTNLI394qJnV\nd6k0zcAcB0clsYDX5uXUAd8/NYsZuz0fziXOB5SkcalKpAjUIgFdUBxRS+r+Gdtr\ns7pL9jJwCroLdLUECKcZxWoEaufBL0RWWY7hjA0nv1qGGVndHKOhSExhwQKBgQCy\nSdrIjcdDSI1gd8d8Q2sk5tRjZNsj4ZSqPcCBROJVjNiOl99KhuoHWvlJ8zDC6oPj\nJ3UW3PkWmyDQtavKaUADgtox7jrIvlwaFK+qhlYv/TUp1wBxDpCebk3VGxkj+d5Z\nRkUvFwrrfaOE8JKn6ogRd2jHBcxKmW2+aQS3svpDQwKBgCI6iW9poywK30GNc4tb\nhlq2mfix0+1it9e4c7WkQnNfLAFG/DbtdHIo6w1IrL0HdWYxNvUzh6AiA48xCKQi\n8INYDQI32jzF0DM3tJ1R310+BJ8RRxRLRfEwR9cGWfJp9mUR4rT04wmop1unV2Ai\n6Kbh94DQuHzZh5C71uw0Wlvz\n-----END PRIVATE KEY-----\n",
  "client_email": "jeevan-config@spread-sheet-444418.iam.gserviceaccount.com",
  "client_id": "102733865930014132790",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/jeevan-config%40spread-sheet-444418.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
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
