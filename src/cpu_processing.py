import cv2
import pytesseract
import torch
import torchvision.transforms as transforms
from torchvision import models
import os
import faiss
import numpy as np
import pandas as pd
from PIL import Image


# Paths
IMAGE_FOLDER = "trademark_images"
CSV_FILE = "trademark_extracted_data.csv"

# Load ResNet18 Model for Feature Extraction
resnet = models.resnet18(pretrained=True)
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])  # Remove final classification layer
resnet.eval()  # Set model to inference mode

# Image Preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Function to Extract Features from an Image
def extract_features(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"⚠️ Error loading image: {image_path}")
        return None

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR (OpenCV) to RGB
    image = Image.fromarray(image)  # Convert to PIL Image

    image = transform(image).unsqueeze(0)  # Apply transformations & add batch dim
    with torch.no_grad():
        feature = resnet(image).squeeze().numpy()
    return feature.flatten()


# Function to Extract Text from Image
def extract_text(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to remove noise
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Apply Adaptive Thresholding (Better for OCR)
    gray = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Use Tesseract OCR with improved config
    custom_config = "--psm 6 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    text = pytesseract.image_to_string(gray, config=custom_config)

    return text.strip()



# Process Images: OCR + Feature Extraction
def process_images():
    image_data = []
    feature_list = []

    for img_file in os.listdir(IMAGE_FOLDER):
        img_path = os.path.join(IMAGE_FOLDER, img_file)
        print(f"🖼️ Processing {img_file}...")

        # Extract text using OCR
        extracted_text = extract_text(img_path)

        # Extract image features using ResNet18
        image_features = extract_features(img_path)

        if image_features is not None:
            feature_list.append(image_features)
            image_data.append({
                "Image File": img_file,
                "Extracted Text": extracted_text
            })

    # Convert to Pandas DataFrame
    df = pd.DataFrame(image_data)
    df.to_csv("trademark_image_text.csv", index=False)
    print("📁 Text & Image Data Saved to `trademark_image_text.csv`")

    # Save FAISS Index for Searching Similar Trademarks
    if feature_list:
        feature_matrix = np.array(feature_list, dtype=np.float32)
        index = faiss.IndexFlatL2(feature_matrix.shape[1])  # L2 distance index
        index.add(feature_matrix)
        faiss.write_index(index, "trademark_faiss.index")
        print("🔍 FAISS Index Saved for Similarity Search")

# Run Processing
if __name__ == "__main__":
    process_images()
