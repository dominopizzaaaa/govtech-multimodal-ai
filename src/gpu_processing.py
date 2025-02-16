import os
import re
from lmdeploy import pipeline, TurbomindEngineConfig
from lmdeploy.vl import load_image

# Define the model and configuration
model = "OpenGVLab/InternVL2_5-8B"
engine_config = TurbomindEngineConfig(session_len=8192)
pipe = pipeline(model, backend_config=engine_config)

# Define folders
IMAGE_FOLDER = "trademark_images"
OUTPUT_FOLDER = "gpu_outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to clean extracted text and ensure last line contains search terms
def extract_searchable_words(text):
    """Extracts words and formats them for search indexing."""
    lines = text.strip().split("\n")

    # Ensure last line exists and is formatted correctly
    if lines:
        last_line = lines[-1]  # Take the last line of the output
        words = re.findall(r"[\w\u4e00-\u9fff]+", last_line)  # Keep words + Chinese characters

        if words:
            spaced_version = ",".join(words)  # Separate words by commas
            merged_version = "".join(words)  # Merge them into one continuous string

            return f"{spaced_version},{merged_version}"  # Ensure both versions are saved

    return ""  # Fallback if no valid words are found

# Function to process images using InternVL2
def process_image(image_path):
    print(f"🖼️ Processing {image_path} with InternVL2...")

    try:
        # Load and process the image
        image = load_image(image_path)

        prompt_text = (
            "Extract the brand name and all words from this image, including Chinese characters. "
            "Do NOT add extra phrases like 'The text is...' or 'The extracted text is...'. "
            "Only output the words. If compound words exist (e.g., 'SyncTalk'), break them into separate words "
            "(e.g., 'sync,talk,synctalk'). Ensure that the last line contains only the extracted words, "
            "strictly formatted as a single line separated by commas. "
            "Additionally, include both the space-separated and merged versions of the text in the final output."
        )

        # Process the image with the pipeline
        result = pipe((prompt_text, image))  # Ensure tuple format

        # Verify result type and extract text properly
        if hasattr(result, "text") and isinstance(result.text, str):
            extracted_text = result.text.strip()
        else:
            raise ValueError("Unexpected response format from InternVL2 model")

        # Extract and format searchable words
        search_terms = extract_searchable_words(extracted_text)

        # Ensure proper filename handling for both .jpg and .png
        output_file = os.path.join(
            OUTPUT_FOLDER, os.path.splitext(os.path.basename(image_path))[0] + ".txt"
        )

        # Save the output to a text file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(search_terms)

        print(f"✅ Saved result to {output_file}: {search_terms}")

    except Exception as e:
        print(f"⚠️ Error processing {image_path}: {e}")

# Process all images in the folder
if __name__ == "__main__":
    for img_file in os.listdir(IMAGE_FOLDER):
        if img_file.lower().endswith((".jpg", ".png")):
            process_image(os.path.join(IMAGE_FOLDER, img_file))