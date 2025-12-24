import gspread
from oauth2client.service_account import ServiceAccountCredentials


GOOGLE_SHEET_CREDENTIALS = {
  "type": "service_account",
  "project_id": "spread-sheet-444418",
  "private_key_id": "311279265ded4972fedb03f25f236d0dde2485b4",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQCryiw0m20PEHzG\n73adpJwIelFejnxLs54kirCnncbuB+R2QEaUnrbFHgVT5RXslyiodyLsq2JZwEMm\nAEiRmNJSx81RvwbmjJb7Eh8kqpLHCH6qihkSBhs1xxuo+OElNHcq9D9XPieX9gmo\n5u9lg0cFI8Quc9DYf8FsCz+q0K6E92ZKoD1DaP5klRhVyoz7SES6n0IEDbYAlpK9\nwccD+whQSuKJbEpj8V8NfHaxsJq2vclzAlGTpJmOScjnGbl5v7tnc+FrZ82CkAfs\nWHtsLcnfl5Xe7nMzYvAzA1zf8dlehlibMjq6DCIxvFco2T2LodRPojqpwURd28Vn\nP5Wsc+iVAgMBAAECgf9guxzcT0HzLMivbw2badUL8QdgXVrsq92gaRFcg7sMzRgX\nsQANL4ShLQZS9x7uDMkYEzCj+anaxifWF5+R9dTerlX7Poh9ySw6s5/vRYNG3CgQ\nXzJx5uS4PPH8po25vveORROYstoYkLHGKXZWv4gXnMwawmjjf3LdihGPkKUauRR0\nyNb/fu6fmCwvhb1fYl/KIcx6sEUnISR+vlTxPkEuT7QCvg5bxNJojwRamUBh/Nzd\nsEsRds7ldTplk7msBcQUPm7hb2FN0TSANZxJeZvx6W6uWjNeO54+AgnOhcucKuAV\nKCYXMgAnzvAHrlCTy+jZ7DO/Bcq7YTkRS0PdDDECgYEA1+tFV/hNURf6+qU5tUxf\nCeEXRJDKejio4S/fMTDb7bwPxW7MgKrAJ/73bXVcnkV2n0Tcmvkt6DZDHLzD5oCH\npq8fSxLTEsZSIcdpcctdn2oHAths1i+JvGNpNigUloSqV7/Nu+rkLMl0BQHMfpJQ\nyHODtbLHs7khH4dbWWNCTFECgYEAy63TT4ZcWyDd9qebL8cy2QrkF7bFO4ekAC8q\nBMGsS6QCIns+FQVskN7IHvftU/ChkUQqlKvEE4i/JeWZAPjHa3ilXs4GuZm0bRUw\n54llhzdH+qnUfiqXyK2L+ni1668JZ4FifGqPbAmyzM0Q7cFEGvWL6Rf2kSsKHLBa\n/LHF+wUCgYBT4KaghOnsLcem5NalMlTdLp7uWNz/W9FnIUSwBE37bYom5WL2PN7G\n6spNsEDZjxyExKh6X4BQ6/toR4BGo/mObAtZC6gJbBdt3dx9g0YMbpDorxCgp/j2\nwRuXGTzeOA1AZ1dRv+8B4wR6CXfaV5agOBebVyczDyDp8ZgwAlo38QKBgQDCo2Yf\nxOJVI1956kleqxloWAQItVxduw16L5gT25Bu6Fgx41w8cmaBOqQ7E+n0ISwEygN2\n9330vOUNrg884oCPr0c5BeFfVAcbhvipCp+/S5C5dbnep41M9Kuju979TtPJ2dbn\n1l0gfVQkaoMW8W3H5YbCRWgW6e5L5CvO94OekQKBgBCwa6oZOgc3z3KlOp8JM5eb\nHORBJo68eED977W9N5F5aCWVz51usPwuERIonLPIBHPaa3W3JQmWxZidKI/eokPN\nHCrGM9TyX6VwYooi8fmVL5KD3SWcoTwqA/41vMk+gGs9HE+/TGVFQhgVh+DsHJA3\nn7+cXqx1hK1IHCjbiU2Q\n-----END PRIVATE KEY-----\n",
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
