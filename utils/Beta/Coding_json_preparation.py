import uuid
import json


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
