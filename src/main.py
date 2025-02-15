import os
import subprocess

# Define script paths
GPU_PROCESSING_SCRIPT = "src/gpu_processing.py"
DATA_SEARCHING_SCRIPT = "src/data_searching.py"

# Ensure necessary directories exist
REQUIRED_FOLDERS = ["trademark_images", "gpu_outputs", "final-result", "data"]

for folder in REQUIRED_FOLDERS:
    os.makedirs(folder, exist_ok=True)

# Step 1: Run GPU Processing
print("🚀 Running GPU processing to extract words from trademark images...")
gpu_process = subprocess.run(["python", GPU_PROCESSING_SCRIPT], capture_output=True, text=True)

# Print GPU processing logs
print("📄 GPU Processing Output:\n", gpu_process.stdout)
if gpu_process.stderr:
    print("⚠️ GPU Processing Error:\n", gpu_process.stderr)

# Step 2: Run Data Searching
print("🔎 Running data searching to find matching trademark data...")
search_process = subprocess.run(["python", DATA_SEARCHING_SCRIPT], capture_output=True, text=True)

# Print Data Searching logs
print("📄 Data Searching Output:\n", search_process.stdout)
if search_process.stderr:
    print("⚠️ Data Searching Error:\n", search_process.stderr)

print("✅ Process completed! Check `final-result/` for outputs.")
