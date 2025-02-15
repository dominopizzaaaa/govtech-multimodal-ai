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

# Function to find the best matching rows (limit to top 2)
def find_best_matches(keyword):
    """ Search for a keyword in 'Mark Name' and return up to 2 best matches. """
    matches = df[df["Mark Name"].str.contains(keyword, case=False, na=False)]
    return matches.head(2)  # Keep only the top 2 matches

# Process each text file in gpu_outputs/
for txt_file in os.listdir(GPU_OUTPUTS_FOLDER):
    if txt_file.endswith(".txt"):
        file_path = os.path.join(GPU_OUTPUTS_FOLDER, txt_file)
        output_file = os.path.join(FINAL_RESULTS_FOLDER, txt_file)  # Keep same name

        with open(file_path, "r", encoding="utf-8") as f:
            extracted_words = f.read().strip().split(",")  # Extract keywords
        
        # Find matching rows in CSV
        matched_rows = pd.DataFrame()
        for word in extracted_words:
            match = find_best_matches(word)
            if not match.empty:
                matched_rows = pd.concat([matched_rows, match])  # Store all matches

        # Remove duplicates and limit to top 2 results
        matched_rows = matched_rows.drop_duplicates(subset=["Application Number"]).head(2)

        # Save results as a TXT file with Post Name, Description & Image URL
        with open(output_file, "w", encoding="utf-8") as f:
            if not matched_rows.empty:
                for _, row in matched_rows.iterrows():
                    mark_name = row["Mark Name"] if pd.notna(row["Mark Name"]) else "Unknown Mark"
                    description = row["Trademark Description"] if pd.notna(row["Trademark Description"]) else "No description available."
                    image_url = row["Trademark Image URL"] if pd.notna(row["Trademark Image URL"]) else "No image available."
                    
                    # Write to TXT file
                    f.write(f"Post Name: {mark_name}\n")
                    f.write(f"Trademark Description: {description}\n")
                    f.write(f"Trademark Image URL: {image_url}\n\n")
                
                print(f"✅ Saved top 2 results to {output_file}")
            else:
                f.write("⚠️ No match found in CSV.\n")
                print(f"⚠️ No match found for {txt_file}")
