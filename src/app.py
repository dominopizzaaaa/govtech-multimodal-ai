import os
import base64
import uvicorn
import subprocess
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Dict

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

# API Model for Request
class ImageInput(BaseModel):
    image: str  # Base64-encoded image

# Helper function to decode and save base64 image
def save_base64_image(base64_string: str, filename: str) -> str:
    image_path = os.path.join(IMAGE_FOLDER, filename)
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(base64_string))
    return image_path

# API Inference Endpoint
@app.post("/invoke")
def invoke_model(data: ImageInput) -> Dict:
    # Generate filename for the image
    filename = "uploaded_image.jpg"
    image_path = save_base64_image(data.image, filename)

    # Step 1: Run GPU Processing (Text Extraction)
    print("🚀 Running GPU processing...")
    subprocess.run(["python", "src/gpu_processing.py"])

    # Step 2: Run Data Searching (Find Matching Trademarks)
    print("🔎 Running data searching...")
    subprocess.run(["python", "src/data_searching.py"])

    # Step 3: Read the output file
    result_file = os.path.join(FINAL_RESULTS_FOLDER, filename.replace(".jpg", ".txt"))
    if os.path.exists(result_file):
        with open(result_file, "r", encoding="utf-8") as f:
            output_data = f.read()
    else:
        output_data = "No match found."

    return {
        "wordsInMark": output_data.split("\n")[0],
        "chineseCharacter": output_data.split("\n")[1] if len(output_data.split("\n")) > 1 else "",
        "descrOfDevice": output_data.split("\n")[2] if len(output_data.split("\n")) > 2 else ""
    }

# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
