# Use an official Python runtime as a parent image
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Set environment variables to prevent prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3-dev \
    libgl1-mesa-glx libglib2.0-0 \
    tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim \
    wget curl git unzip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose FastAPI application port
EXPOSE 8000

# Set environment variables for Hugging Face API (if needed)
ENV HF_HOME="/root/.cache/huggingface"
ENV CUDA_VISIBLE_DEVICES=0

# Define the command to run FastAPI
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
