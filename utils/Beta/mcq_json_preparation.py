import uuid
import json

def mcq_practice_prepare_json(resource_id, title, duration, parent_id, child_order, description, total_score, pass_score, order_type, no_questions):
    """
    Prepare JSON data based on the user inputs, formatted for Google Sheets upload.
    This includes several rows for descriptive purposes and additional instructions.
    """
    common_unit_id = str(uuid.uuid4())

    json_data = {
        "ResourcesData": {
            "headers": [
                "resource_id",
                "resource_type",
                "dependent_resource_count",
                "dependent_resources",
                "dependent_reason_display_text",
                "parent_resource_count",
                "child_order",
                "parent_resources",
                "auto_unlock"
            ],
            "rows": [
                [
                    resource_id,
                    "UNIT",
                    0.0,
                    "",
                    "",
                    1.0,
                    " ",
                    " ",
                    True
                ],
                [
                    " ",
                    " ",
                    " ",
                    "",
                    "",
                    " ",
                    child_order,
                    parent_id,
                    " "
                ]
            ]
        },
        "Units": {
            "headers": [
                "unit_id",
                "common_unit_id",
                "unit_type",
                "duration_in_sec",
                "unit_tags"
            ],
            "rows": [
                [
                    resource_id,
                    common_unit_id,
                    "PRACTICE",
                    duration,
                    ""
                ]
            ]
        },
        "Exam": {
            "headers": [
                "exam_id",
                "title",
                "description",
                "exam_content_type",
                "exam_duration",
                "max_number_of_attempts",
                "question_jumbling",
                "should_send_solutions",
                "time_limit",
                "correct_answer_score",
                "wrong_answer_score",
                "solved_correct_score",
                "solved_incorrect_score",
                "unsolved_correct_score",
                "unsolved_incorrect_score",
                "skip_enabled",
                "skip_enabled_time",
                "max_repeat_count",
                "hint_enabled",
                "example_enabled",
                "solution_enabled",
                "multiple_submissions_enabled",
                "submission_selection_type",
                "show_answer_enabled",
                "show_answer_scoring_mode",
                "answer_seen_scoring_mode",
                "user_response_scoring_mode",
                "total_scoring_mode",
                "score_masking_config",
                "min_correct_questions",
                "min_total_score",
                "question_picking_mode",
                "order",
                "no_of_levels",
                "order_of_levels",
                "level",
                "level_scoring",
                "solved_percent",
                "is_leaderboard_enabled",
                "is_zone_config_enabled",
                "no_of_zones",
                "zone_id",
                "zone_name",
                "zone_colour",
                "zone_order",
                "no_of_stars",
                "total_stars",
                "no_of_users",
                "min_percentage",
                "max_percentage",
                "no_of_instructions",
                "instruction",
                "time_gap_between_attempts",
                "total_max_score",
                "min_score_to_pass",
                "options_ordering_type",
                "should_send_hints",
                "questions_picking_type"
            ],
            "rows": [
                [
                    resource_id, title, description, "PRIMITIVE_CODING", duration, 1, "on", "yes", duration, 1, 0, 0, 0,
                    0, 0, "on", 10, 3, "off", "off", "off", "off", "BEST", "on", "INCORRECT", "DEFAULT", "DEFAULT",
                    "DEFAULT", " ", " ", " ", "COMPLETION_STATE_BASED_ORDER", "UNANSWERED | SKIPPED", " ", " ", " ", " ", 0,
                    "NO", "NO", " ", " ", " ", " ", " ", " ", " ", " ", " ", "", 4, " ", " ", total_score, pass_score, order_type, " ", " ",
                ],
                [" ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ",
                 " ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " "," ", " ", " ", " "," ",
                 "<b>Number of Questions: </b> " + str(no_questions), " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ",
                 " ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " "," ", " ", " ", " "," ",
                 "<b>Types of Questions: </b>MCQs", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ",
                 " ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " "," ", " ", " ", " "," ",
                 "<b>Marking Scheme: </b>All questions have equal weightage. Every correct response gets +1 mark. There is no negative marking.", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ",
                 " ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " ", " ", " ", " "," ", " "," ", " ", " ", " "," ",
                 "You must answer all the MCQs correctly in order to mark your practice as completed.", " ", " ", " ", " ", " "]
            ]
        }
    }

    return json_data
