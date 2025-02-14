# Use a base image with Python and CUDA for GPU processing
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Set up environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface \
    TORCH_HOME=/root/.cache/torch

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy project files
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Hugging Face CLI and log in
RUN huggingface-cli login --token $HF_TOKEN

# Expose port for API (if applicable)
EXPOSE 8000

# Command to run GPU processing script
CMD ["python", "src/gpu_processing.py"]
