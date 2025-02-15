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

When I ran on my first try, I was so surprised at the accuracy and ability of InternVL to decipher not only the words, but also the background. For example, it was able to tell the background was depicting great wall of china, which I found very fascinating (maybe because I was using CPU the whole time to try to figure ut the words which is much less effective at doing so). It was also able to tell, output and translate korean words and find the company. The accuracy was so much higher than that of CPU as seen below. As this is my first time using InternVL, I did not change the output and the defaulted output was given to me, which was a description of the image. I plan to change the prompt so that I will be able to obtain keywords and the mark name to be able to query the data later for the second iteration.

#### Accuracy achieved: (To be added later)
- First try: 23/28
- Second try (changed input prompt: "Analyze this image and provide the following details: \n"
            "1. Company or Brand Name: Identify the most likely brand or company associated with this logo.\n"
            "2. Text Extraction and Indexing: Extract all visible text and format it for optimal search indexing. \n"
            "   - If there are compound words (e.g., 'SyncTalk'), break them down into separate words (e.g., 'sync talk synctalk').\n"
            "   - If there is Chinese text, provide a pinyin transliteration to improve searchability."): 24/28
- Third try: I change the prompt to 'extract only the brand name' so i can use the brand names to search for the data later: 24/28. Chinese characters not captured
- Fourth try: I made the prompt more detailed: by adding 'do not add extra words'. Too many phrases like: here are the words extracted from the image and also chinese characters still not captured: 18/28
- Fifth try: Changed prompted to "Extract the brand name and words from this image. Do not add extra phrases like 'the text in the image is ...' or 'extracted text is ...' or 'the words in the image are'. I should not see any of those phrases or any phrase that carries the same meaning and purpose. I only want the words in the picture. Output Chinese characters and punctuation if present in the photo. Include all words that are in the photo": 20/28
- Sixth try: I realised my second try is doing the best so far at extracting chinese words, so i decided to reuse that prompt and add onto it. "Analyze this image and provide the following details: \n"
            "1. Company or Brand Name: Identify the most likely brand or company associated with this logo.\n"
            "2. Text Extraction and Indexing: Extract all visible text and format it for optimal search indexing. \n"
            "   - If there are compound words (e.g., 'SyncTalk'), break them down into separate words (e.g., 'sync talk synctalk').\n"
            "   - If there is Chinese text, provide a pinyin transliteration to improve searchability.
            Lastly, I want all the words to be searched to be placed at the last row, separated by only a comma (not white spaces). this includes all the texts found from point 1 and 2": 25/28 best result.
            
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
