import os
import pandas as pd

# Define file paths
CSV_FILE = "data/trademark_extracted_data.csv"
GPU_OUTPUTS_FOLDER = "gpu_outputs"
FINAL_RESULTS_FOLDER = "final-result"

# Ensure output directory exists
os.makedirs(FINAL_RESULTS_FOLDER, exist_ok=True)

# Load CSV data
df = pd.read_csv(CSV_FILE)

# Columns to extract from CSV
columns_to_extract = ["Application Number", "Filing Date", "Mark Name", "Trademark Description", 
                      "Goods and Services", "Applicant Name", "Applicant Country", 
                      "Trademark Image URL", "Saved Image File", "Status", "Expiry Date"]

# Function to search for a match in the CSV file
def find_matching_row(keyword):
    """ Search for a keyword in the CSV 'Mark Name' and return the matched row. """
    match = df[df["Mark Name"].str.contains(keyword, case=False, na=False)]
    return match

# Process each text file in gpu_outputs/
for txt_file in os.listdir(GPU_OUTPUTS_FOLDER):
    if txt_file.endswith(".txt"):
        file_path = os.path.join(GPU_OUTPUTS_FOLDER, txt_file)
        output_file = os.path.join(FINAL_RESULTS_FOLDER, txt_file)  # Save under same name

        with open(file_path, "r", encoding="utf-8") as f:
            extracted_words = f.read().strip().split(",")  # Extract keywords
        
        # Find matching row in CSV
        matched_rows = pd.DataFrame()
        for word in extracted_words:
            match = find_matching_row(word)
            if not match.empty:
                matched_rows = pd.concat([matched_rows, match])  # Store all matches
        
        # Remove duplicates
        matched_rows = matched_rows.drop_duplicates(subset=["Application Number"])
        
        # Save results
        if not matched_rows.empty:
            matched_rows.to_csv(output_file, index=False, columns=columns_to_extract)
            print(f"✅ Saved result to {output_file}")
        else:
            print(f"⚠️ No match found for {txt_file}")
