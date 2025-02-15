import os
import re
import pandas as pd

# Define file paths
CSV_FILE = "data/trademark_extracted_data.csv"
GPU_OUTPUTS_FOLDER = "gpu_outputs"
FINAL_RESULTS_FOLDER = "final-result"

# Ensure output directory exists
os.makedirs(FINAL_RESULTS_FOLDER, exist_ok=True)

# Load CSV data, ensuring NaN values are replaced with empty strings
df = pd.read_csv(CSV_FILE, dtype=str).fillna("")  # Convert all columns to strings and replace NaN with ""

# Function to extract and remove duplicate Chinese phrases
def extract_unique_chinese(text):
    """ Extracts only unique Chinese characters/phrases from text. """
    chinese_phrases = re.findall(r'[\u4e00-\u9fff]+', text)  # Find all Chinese characters
    unique_phrases = list(dict.fromkeys(chinese_phrases))  # Remove duplicates while keeping order
    return " ".join(unique_phrases) if unique_phrases else "N/A"  # Return formatted text

# Function to find best matches in the CSV file
def find_best_matches(keywords):
    """ Finds the top two best matches based on 'Mark Name'. """
    matched_rows = pd.DataFrame()

    for word in keywords:
        matches = df[df["Mark Name"].str.contains(word, case=False, na=False)]
        if not matches.empty:
            matched_rows = pd.concat([matched_rows, matches])

    # Drop duplicate matches and keep only the top 2 most relevant ones
    matched_rows = matched_rows.drop_duplicates(subset=["Application Number"]).head(2)
    
    return matched_rows

# Process each text file in gpu_outputs/
for txt_file in os.listdir(GPU_OUTPUTS_FOLDER):
    if txt_file.endswith(".txt"):
        file_path = os.path.join(GPU_OUTPUTS_FOLDER, txt_file)
        output_file = os.path.join(FINAL_RESULTS_FOLDER, txt_file)  # Save under same name

        with open(file_path, "r", encoding="utf-8") as f:
            extracted_text = f.read().strip()  # Read the GPU output

        # Extract English keywords and unique Chinese characters separately
        extracted_words = extracted_text.split(",")  # Split words by comma
        unique_chinese_characters = extract_unique_chinese(extracted_text)  # Extract unique Chinese characters

        # Find best matching rows in CSV
        matched_rows = find_best_matches(extracted_words)

        # Prepare the output data
        if not matched_rows.empty:
            output_lines = []
            for _, row in matched_rows.iterrows():
                mark_name = str(row.get("Mark Name", "")).strip()
                description = str(row.get("Trademark Description", "")).strip()
                image_url = str(row.get("Trademark Image URL", "")).strip()

                output_lines.append(
                    f"Mark Name: {mark_name}\n"
                    f"Description: {description}\n"
                    f"Image URL: {image_url}\n"
                    f"Chinese Characters: {unique_chinese_characters}\n"
                )

            # Save results to text file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines))

            print(f"✅ Saved result to {output_file}")
        else:
            print(f"⚠️ No match found for {txt_file}")
