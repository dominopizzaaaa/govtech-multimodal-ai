import os
import re
import time
from gradio_client import Client, handle_file

HF_API_TOKEN = "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"

# Define API Client for Hugging Face InternVL2 with Premium Access
client = Client("developer0hye/InternVL2_5-8B", hf_token=HF_API_TOKEN)

# Define folders
IMAGE_FOLDER = "trademark_images"
OUTPUT_FOLDER = "gpu_outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to clean extracted text and remove redundant words
def clean_brand_name(text):
    """ Cleans text to extract only the brand name and format correctly. """
    text = text.lower().strip()

    # Remove common incorrect phrases
    text = re.sub(r"^(the\s+brand\s+name\s+is\s+)", "", text)

    # Keep only alphanumeric characters and spaces
    words = re.findall(r'[a-z0-9]+', text)
    spaced_version = " ".join(words)
    merged_version = "".join(words)
    
    return spaced_version, merged_version

# Function to process images using InternVL2 API
def process_image(image_path):
    print(f"Processing {image_path} with InternVL2...")

    try:
        # Extract text using InternVL2 API
        extracted_text = client.predict(
            media_input=handle_file(image_path),
            text_input="Extract the brand name from this image. Do not add extra words or formatting. Do not add extra phrases like 'the text in the image is ...' or 'extracted text is ...' or 'the words in the image are'. I should not see any of those phrases or any phrase that carries the same meaning and purpose. Keep Chinese characters, punctuation, and English words exactly as they appear. Ensure all words, including Chinese, are extracted and formatted correctly.",
            api_name="/internvl_inference"
        ).strip()

        # Clean and format the extracted brand name
        spaced_name, merged_name = clean_brand_name(extracted_text)

        # Save only the correct brand name
        output_text = f"{spaced_name} {merged_name}"
        output_file = os.path.join(OUTPUT_FOLDER, os.path.basename(image_path).replace(".jpg", ".txt"))
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_text)
        
        print(f"✅ Saved result to {output_file}: {output_text}")

    except Exception as e:
        print(f"⚠️ Error processing {image_path}: {e}")

        # Handle API Rate Limit (Wait and Retry)
        if "exceeded your GPU quota" in str(e):
            print("⏳ Waiting 60 seconds before retrying...")
            time.sleep(60)  # Wait for quota reset
            process_image(image_path)  # Retry request

# Process all images in the folder
if __name__ == "__main__":
    for img_file in os.listdir(IMAGE_FOLDER):
        if img_file.lower().endswith((".jpg", ".png")):
            process_image(os.path.join(IMAGE_FOLDER, img_file))
