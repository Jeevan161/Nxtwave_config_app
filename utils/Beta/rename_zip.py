import zipfile
import os
import shutil
import json


def rename_json_files_in_zip(zip_file, output_dir, uuid):
    """
    Rename all JSON files in the provided ZIP to {uuid}.json.
    Retains folder structure and processes all subfolders recursively.
    Validates `question_id` values and aggregates errors if any are found.
    Does not create a ZIP if validation fails.
    """
    temp_extract_dir = os.path.join(output_dir, 'temp_extract')
    temp_output_dir = os.path.join(output_dir, 'temp_output')

    # Create temporary directories for extraction and output
    os.makedirs(temp_extract_dir, exist_ok=True)
    os.makedirs(temp_output_dir, exist_ok=True)

    # Extract the uploaded zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)

    # Initialize counters and error tracking
    total_questions = 0
    validation_errors = []

    # Walk through the extracted files, rename JSON files to {uuid}.json, and validate them
    for dirpath, _, filenames in os.walk(temp_extract_dir):
        for filename in filenames:
            if filename.endswith('.json'):  # Only process JSON files
                src_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(src_path, temp_extract_dir)  # Retain structure
                dest_path = os.path.join(temp_output_dir, os.path.dirname(relative_path), f"{uuid}.json")

                # Create destination folder structure
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                # Validate and count question_id occurrences in the JSON file
                with open(src_path, 'r') as json_file:
                    try:
                        data = json.load(json_file)
                        question_ids = [item.get('question_id') for item in data if 'question_id' in item]

                        # Check for empty question_id values
                        invalid_questions = [qid for qid in question_ids if not qid]
                        if invalid_questions:
                            subfolder_name = os.path.relpath(dirpath, temp_extract_dir)
                            validation_errors.append(
                                f"Empty question_id values found in file: {filename} in subfolder: {subfolder_name}"
                            )

                        total_questions += len(question_ids)
                    except json.JSONDecodeError:
                        validation_errors.append(f"Invalid JSON format in file: {filename}")

                # Copy the renamed JSON file to the output directory (even if there are validation errors)
                shutil.copy(src_path, dest_path)

    # If there are validation errors, do not create the final ZIP
    if validation_errors:
        # Cleanup temporary directories
        shutil.rmtree(temp_extract_dir)
        shutil.rmtree(temp_output_dir)

        return {"errors": validation_errors, "total_questions": total_questions}

    # Create the final zip file with renamed JSONs and the original structure
    final_zip_path = os.path.join(output_dir, f"modified_{uuid}.zip")
    with zipfile.ZipFile(final_zip_path, 'w') as new_zip:
        for dirpath, _, filenames in os.walk(temp_output_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                arcname = os.path.relpath(file_path, temp_output_dir)  # Retain folder structure in zip
                new_zip.write(file_path, arcname)

    # Cleanup temporary directories
    shutil.rmtree(temp_extract_dir)
    shutil.rmtree(temp_output_dir)

    return {"zip_path": final_zip_path, "total_questions": total_questions}
