import gspread
from oauth2client.service_account import ServiceAccountCredentials

from utils.Beta.sheet_preparation import authorize_google_sheets


def upload_to_google_sheets_single_sheet(tutorial_data, additional_data, title, request_mail):
    """
    Uploads the processed JSON data (Tutorial + TutorialStep) and additional data (ResourcesData, Units, etc.)
    to a Google Sheet, creating separate tabs for each section.
    """
    try:
        # Step 1: Authenticate and create a client to interact with Google Sheets
        client = authorize_google_sheets()

        # Step 2: Create a new Google Spreadsheet with the provided name
        spreadsheet = client.create(title)
        print(f"Spreadsheet '{title}' created successfully.")
    except Exception as e:
        print(f"Error creating spreadsheet: {e}")
        return None

    try:
        # Step 3: Share the spreadsheet with editor access
        spreadsheet.share('learningresource@nkblearningbackend.iam.gserviceaccount.com', perm_type='user',
                          role='writer')
        print("Editor access granted to 'learningresource@nkblearningbackend.iam.gserviceaccount.com'.")
        spreadsheet.share('jeevansravanth.parisa@nxtwave.co.in', perm_type='user', role='writer')
        print("Editor access granted to 'Jeevan'.")
        spreadsheet.share(request_mail, perm_type='user', role='writer')
    except Exception as e:
        print(f"Error sharing spreadsheet: {e}")
        return None

    try:
        # Step 4: Populate each section into its own tab
        add_section_to_new_tab(spreadsheet, "Tutorial", tutorial_data.get("Tutorial", []))
        add_section_to_new_tab(spreadsheet, "TutorialStep", tutorial_data.get("TutorialStep", []))
        add_section_to_new_tab(spreadsheet, "ResourcesData", additional_data.get("ResourcesData", {}))
        add_section_to_new_tab(spreadsheet, "Units", additional_data.get("Units", {}))
        add_section_to_new_tab(spreadsheet, "LearningResourceSet", additional_data.get("LearningResourceSet", {}))
        add_section_to_new_tab(spreadsheet, "LearningResources", additional_data.get("LearningResources", {}))

        print("Data successfully added to separate tabs in the Google Spreadsheet.")
        return spreadsheet.id  # Return the spreadsheet ID
    except Exception as e:
        print(f"Error populating spreadsheet: {e}")
        return None


def add_section_to_new_tab(spreadsheet, tab_name, section_data):
    """
    Adds a new tab to the spreadsheet and populates it with the given section data.

    Parameters:
        spreadsheet: The Google Spreadsheet object.
        tab_name (str): Name of the tab to create.
        section_data: The data to populate, expected as a dict with 'headers' and 'rows' or a list of rows.
    """
    try:
        # Create a new tab
        worksheet = spreadsheet.add_worksheet(title=tab_name, rows="1000", cols="20")

        if isinstance(section_data, dict):
            # Handle the dictionary format (headers + rows)
            headers = section_data.get("headers", [])
            rows = section_data.get("rows", [])

            if headers:
                worksheet.append_row(headers)
            for row in rows:
                worksheet.append_row(row)
        elif isinstance(section_data, list):
            # Handle the list format (direct rows)
            for row in section_data:
                worksheet.append_row(row)
        else:
            raise ValueError(
                "Invalid section_data format. Expected a dict with 'headers' and 'rows' or a list of rows.")

    except Exception as e:
        print(f"Error adding section '{tab_name}': {e}")
        raise
