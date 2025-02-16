import os
import re
import time
from gradio_client import Client, handle_file

# Use Hugging Face Premium API Token
HF_API_TOKEN = "censored"

# Initialize API Client for Hugging Face InternVL2 (refer to README point 5)
client = Client("developer0hye/InternVL2_5-8B", hf_token=HF_API_TOKEN)

# Define folders
IMAGE_FOLDER = "trademark_images"
OUTPUT_FOLDER = "gpu_outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to clean extracted text and ensure last line contains search terms
def extract_searchable_words(text):
    """ Extracts words and formats them for search indexing. """
    lines = text.strip().split("\n")
    
    # Ensure last line exists and is formatted correctly
    if lines:
        last_line = lines[-1]  # Take the last line of the output
        words = re.findall(r'[\w\u4e00-\u9fff]+', last_line)  # Keep words + Chinese characters
        
        if words:
            spaced_version = ",".join(words)  # Separate words by commas
            merged_version = "".join(words)  # Merge them into one continuous string
            
            return f"{spaced_version},{merged_version}"  # Ensure both versions are saved
    
    return ""  # Fallback if no valid words are found

# Function to process images using InternVL2 API
def process_image(image_path):
    print(f"Processing {image_path} with InternVL2...")

    try:
        # Extract text using InternVL2 API
        extracted_text = client.predict(
            media_input=handle_file(image_path),
            text_input=(
                "Extract the brand name and all words from this image, including Chinese characters. "
                "Do NOT add extra phrases like 'The text is...' or 'The extracted text is...'. "
                "Only output the words. If compound words exist (e.g., 'SyncTalk'), break them into separate words "
                "(e.g., 'sync,talk,synctalk'). Ensure that the last line contains only the extracted words, "
                "strictly formatted as a single line separated by commas. "
                "Additionally, include both the space-separated and merged versions of the text in the final output."
            ),
            api_name="/internvl_inference"
        ).strip()

        search_terms = extract_searchable_words(extracted_text)

        # Ensure proper filename handling for both .jpg and .png
        output_file = os.path.join(
            OUTPUT_FOLDER, os.path.splitext(os.path.basename(image_path))[0] + ".txt"
        )
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(search_terms)
        
        print(f"✅ Saved result to {output_file}: {search_terms}")

    except Exception as e:
        print(f"⚠️ Error processing {image_path}: {e}")

        # Handle API Rate Limit (Wait and Retry)
        if "exceeded your GPU quota" in str(e).lower():
            print("⏳ Waiting 60 seconds before retrying...")
            time.sleep(60)  # Wait for quota reset
            process_image(image_path)  # Retry request

# Process all images in the folder
if __name__ == "__main__":
    for img_file in os.listdir(IMAGE_FOLDER):
        if img_file.lower().endswith((".jpg", ".png")):
            process_image(os.path.join(IMAGE_FOLDER, img_file))
