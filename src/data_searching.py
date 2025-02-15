import os
import re
import pandas as pd

# Define file paths
DATA_FOLDER = "data"
GPU_OUTPUTS_FOLDER = "gpu_outputs"
FINAL_RESULTS_FOLDER = "final-result"

# Ensure output directory exists
os.makedirs(FINAL_RESULTS_FOLDER, exist_ok=True)

# Load all CSV data from the `data/` folder
def load_all_csv_data():
    """ Loads all yearly CSV files and merges them into one DataFrame. """
    all_files = [os.path.join(DATA_FOLDER, f) for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
    
    if not all_files:
        print("⚠️ No CSV files found in the 'data/' folder. Starting with an empty dataset.")
        return pd.DataFrame(columns=["Application Number", "Mark Name", "Trademark Description", 
                                     "Goods and Services", "Trademark Image URL"])
    
    df_list = [pd.read_csv(file, dtype=str).fillna("") for file in all_files]
    merged_df = pd.concat(df_list, ignore_index=True)
    
    print(f"✅ Loaded {len(all_files)} CSV files into memory.")
    return merged_df

# Function to extract and remove duplicate Chinese phrases
def extract_unique_chinese(text):
    """ Extracts only unique Chinese characters/phrases from text. """
    chinese_phrases = re.findall(r'[\u4e00-\u9fff]+', text)  # Find all Chinese characters
    unique_phrases = list(dict.fromkeys(chinese_phrases))  # Remove duplicates while keeping order
    return " ".join(unique_phrases) if unique_phrases else "N/A"  # Return formatted text

# Function to find best matches in the CSV data
def find_best_matches(df, keywords):
    """ Finds the top two best matches based on 'Mark Name'. """
    if df.empty:
        return pd.DataFrame()  # Return empty DataFrame if no data is available

    matched_rows = pd.DataFrame()

    for word in keywords:
        matches = df[df["Mark Name"].str.contains(word, case=False, na=False)]
        if not matches.empty:
            matched_rows = pd.concat([matched_rows, matches])

    # Drop duplicate matches and keep only the top 2 most relevant ones
    matched_rows = matched_rows.drop_duplicates(subset=["Application Number"]).head(2)
    
    return matched_rows

# Load all CSV data
df = load_all_csv_data()

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

        # Find best matching rows in all CSV files
        matched_rows = find_best_matches(df, extracted_words)

        # Prepare the output data
        if not matched_rows.empty:
            output_lines = []
            for _, row in matched_rows.iterrows():
                mark_name = str(row.get("Mark Name", "")).strip()
                description = str(row.get("Trademark Description", "")).strip()
                image_url = str(row.get("Trademark Image URL", "")).strip()
                
                # If description is empty, use "Goods and Services"
                if not description:
                    description = str(row.get("Goods and Services", "")).strip()

                output_lines.append(
                    f"Mark Name: {mark_name}\n"
                    f"Description: {description}\n"
                    f"Image URL: {image_url}\n"
                    f"Chinese Characters: {unique_chinese_characters}\n"
                    "----------------------"
                )

            # Save results to text file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines))

            print(f"✅ Saved result to {output_file}")
        else:
            print(f"⚠️ No match found for {txt_file}")
