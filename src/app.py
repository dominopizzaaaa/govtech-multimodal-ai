import os
import base64
import uvicorn
import subprocess
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

# Define FastAPI app
app = FastAPI()

# Define folders
IMAGE_FOLDER = "trademark_images"
OUTPUT_FOLDER = "gpu_outputs"
FINAL_RESULTS_FOLDER = "final-result"

# Ensure necessary directories exist
for folder in [IMAGE_FOLDER, OUTPUT_FOLDER, FINAL_RESULTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# API Health Check
@app.get("/ping")
def health_check():
    return {"message": "pong"}

# API Model for Request (Accept Multiple Images)
class ImageInput(BaseModel):
    images: List[str]  # List of Base64-encoded images

# Helper function to decode and save base64 image
def save_base64_image(base64_string: str, filename: str) -> str:
    image_path = os.path.join(IMAGE_FOLDER, filename)
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(base64_string))
    return image_path

# Function to extract structured data correctly
def parse_extracted_text(output_data):
    """ Parses extracted text from the final output file. """
    lines = output_data.strip().split("\n")

    words_in_mark = ""
    chinese_character = ""
    descr_of_device = ""

    for line in lines:
        if line.startswith("Mark Name:"):
            words_in_mark = line.replace("Mark Name:", "").strip()
        elif line.startswith("Description:"):
            descr_of_device = line.replace("Description:", "").strip()
        elif line.startswith("Chinese Characters:"):
            chinese_character = line.replace("Chinese Characters:", "").strip()

    return {
        "wordsInMark": words_in_mark,
        "chineseCharacter": chinese_character if chinese_character and chinese_character.lower() != "n/a" else "",
        "descrOfDevice": descr_of_device
    }

# API Inference Endpoint (Support Multiple Images)
@app.post("/invoke")
def invoke_model(data: ImageInput) -> List[Dict]:
    results = []

    for index, base64_image in enumerate(data.images):
        # Generate a unique filename for each image
        filename = f"uploaded_image_{index}.jpg"
        image_path = save_base64_image(base64_image, filename)

        # Step 1: Run GPU Processing (Text Extraction)
        print(f"🚀 Running GPU processing on {filename}...")
        subprocess.run(["python", "src/gpu_processing.py"])

        # Step 2: Run Data Searching (Find Matching Trademarks)
        print(f"🔎 Running data searching on {filename}...")
        subprocess.run(["python", "src/data_searching.py"])

        # Step 3: Read the output file
        result_file = os.path.join(FINAL_RESULTS_FOLDER, filename.replace(".jpg", ".txt"))
        if os.path.exists(result_file):
            with open(result_file, "r", encoding="utf-8") as f:
                output_data = f.read()
        else:
            output_data = "No match found."

        # Append result for this image
        results.append({
            "image": filename,
            **parse_extracted_text(output_data)  # Extract structured text properly
        })

    return results

# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
