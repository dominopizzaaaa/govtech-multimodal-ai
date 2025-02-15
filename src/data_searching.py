import os
import re
import json
import pandas as pd

# Define file paths
CSV_FILE = "data/trademark_extracted_data.csv"
GPU_OUTPUTS_FOLDER = "gpu_outputs"
FINAL_RESULTS_FOLDER = "final-result"

# Ensure output directory exists
os.makedirs(FINAL_RESULTS_FOLDER, exist_ok=True)

# Load CSV data
df = pd.read_csv(CSV_FILE)
df.columns = df.columns.str.strip()  # Remove extra spaces in column names

# Debug: Check if Trademark Description column exists
if "Trademark Description" not in df.columns:
    raise ValueError("⚠️ 'Trademark Description' column not found in CSV!")

# Function to search for a match in the CSV file
def find_matching_row(keyword):
    """Search for a keyword in 'Mark Name' and return the matched row."""
    match = df[df["Mark Name"].str.contains(keyword, case=False, na=False)]
    return match

# Process each text file in gpu_outputs/
for txt_file in os.listdir(GPU_OUTPUTS_FOLDER):
    if txt_file.endswith(".txt"):
        file_path = os.path.join(GPU_OUTPUTS_FOLDER, txt_file)
        output_file = os.path.join(FINAL_RESULTS_FOLDER, txt_file.replace(".txt", ".json"))

        with open(file_path, "r", encoding="utf-8") as f:
            extracted_words = f.read().strip().split(",")

        # Find matching row in CSV
        matched_rows = pd.DataFrame()
        for word in extracted_words:
            match = find_matching_row(word)
            if not match.empty:
                matched_rows = pd.concat([matched_rows, match])

        # Remove duplicates based on Application Number
        matched_rows = matched_rows.drop_duplicates(subset=["Application Number"])

        # Save results in JSON format
        if not matched_rows.empty:
            # Extract and clean data
            extracted_info = matched_rows[["Trademark Description", "Trademark Image URL"]].fillna("").to_dict(orient="records")

            result_dict = {
                "wordsInMark": ",".join(extracted_words),
                "chineseCharacter": "",  # Placeholder if needed
                "descrOfDevice": extracted_info  # Ensure correct format
            }

            # Debugging: Print first result to confirm
            print(f"🔍 DEBUG: {result_dict}")

            # Save as JSON
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=4, ensure_ascii=False)

            print(f"✅ Saved result to {output_file}")
        else:
            print(f"⚠️ No match found for {txt_file}")
