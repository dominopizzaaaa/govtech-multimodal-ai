# TradeMark Image OCR & AI Processing

## Project Overview
I started this project to explore multimodal AI processing for extracting text from trademark images. Initially, I thought of using traditional OCR, but I quickly realized that some images had stylized fonts, distortions, and even non-Latin characters.

To improve accuracy, I researched different CPU and GPU-based models to process images and extract text. This repository contains my journey through different approaches.

---

## 1. My Initial Approach: CPU Processing
At first, I wanted to test image OCR using only CPU resources. Since my laptop does not have a GPU, I looked for efficient methods to extract text without requiring heavy computation.

### Steps I Took
- I started with Tesseract OCR, which is lightweight and works well for simple images.
- I then explored ResNet18 feature extraction to analyze image embeddings.
- I realized that OCR struggled with Chinese characters and complex fonts, so I had to refine the approach.
- I added Faiss indexing to store extracted image features for similarity searches.

### Challenges Faced in CPU Processing
- OCR was not accurate enough – many extracted texts had errors.
- Processing speed was fine, but text extraction quality needed improvement.
- I realised that some of the outputs have the actual word, but there are many redundant words like for example: "a LES ay 13pm VG vo 2 WW IN BA las ef any iz a is S sf ms Bx a 44tee s4 fL TtsIPNA AYE eModernChinaTeaShop" when the actual word is ModernChinaTeaShop so i tested it out on deepseek to see if it could derive the Mark Name with the garbage that comes with the output: 
![DeepSeek Trial Logo](./trademark_images/deepseek_trial.png)
As seen, using deepseek works, so i tried to incorporate deepseek into my model. However, while running the output and after many iterations of trying different versions of deepseek from hugging face, it took way too much time to process the output and clean up the final text (much more than allowed) so i decided that proceeding with gpu-processing will be a better option

#### Accuracy achieved (CPU): Defined as getting the output without extra characters
- First try: 13/28
- Second try (Improved OCR preprocessing with adaptive thresholding, Gaussian blur, and character whitelist): 15/28
- Third try (Forgot that I had to account for chinese charcters too (brew install tesseract-lang)): 15/28 no change
---

## 2. My Next Step: GPU-Based Processing
Since CPU-based OCR was not sufficient, I researched models that use GPU acceleration for better text extraction. I came across InternVL2 and found that it excels in multimodal vision-language tasks.

### Why I Chose InternVL2
- Better accuracy compared to traditional OCR.
- Handles both English and Chinese characters well.
- Leverages deep learning for complex images rather than just template matching.

### How I Set It Up
1. I first tested InternVL2 on Hugging Face’s free API, but it had a strict quota.
2. I set up a Docker environment to later run on a GPU-powered machine.
3. My friend offered to test it on her local GPU, so I modified the code accordingly.

#### Accuracy achieved: (To be added later)

---

## 3. Running This Project
Depending on whether you have CPU or GPU, you can run the project in different ways.

### Option 1: Running on CPU
```
python src/cpu_processing.py
```
Works for basic OCR, but not as accurate.

### Option 2: Running on GPU (Local)
```
python src/gpu_processing.py
```
Requires InternVL2 locally and a CUDA-enabled GPU.

### Option 3: Running on GPU (Docker)
If using a Docker container on a GPU machine:
```
docker build -t gpu-processing .
docker run --gpus all gpu-processing
```

---

## 4. Next Steps & Improvements
- Fine-tune model to improve accuracy for distorted images.
- Compare InternVL2 with other multimodal models like DeepSeek-VL.
- Optimize runtime performance for large-scale trademark analysis.

---

## 5. Dependencies (requirements.txt)
If you are running this on your own machine, make sure to install:
```
torch
transformers
Pillow
numpy
opencv-python
tesseract
faiss-cpu
huggingface_hub
gradio_client
```

---
