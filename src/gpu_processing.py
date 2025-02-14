import os
from gradio_client import Client, handle_file

# Define API Client for InternVL2
client = Client("developer0hye/InternVL2_5-8B")

# Define the folder containing images
IMAGE_FOLDER = "trademark_images"
OUTPUT_FOLDER = "gpu_outputs"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to process images using InternVL2 API
def process_image(image_path):
    print(f"🖼️ Processing {image_path} with InternVL2...")

    try:
        # Upload image to the API and run inference
        result = client.predict(
            media_input=handle_file(image_path),
            text_input=None,
            api_name="/internvl_inference"
        )

        # Save the output to a text file
        output_file = os.path.join(OUTPUT_FOLDER, os.path.basename(image_path).replace(".jpg", ".txt"))
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        
        print(f"✅ Saved result to {output_file}")

    except Exception as e:
        print(f"⚠️ Error processing {image_path}: {e}")

# Process all images in the folder
if __name__ == "__main__":
    for img_file in os.listdir(IMAGE_FOLDER):
        if img_file.lower().endswith((".jpg", ".png")):
            process_image(os.path.join(IMAGE_FOLDER, img_file))
