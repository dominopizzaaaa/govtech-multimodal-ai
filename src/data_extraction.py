import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta

# API Endpoint
API_URL = "https://api.data.gov.sg/v1/technology/ipos/trademarks"

# File paths
CSV_FILE = "data/trademark_extracted_data.csv"
IMAGE_FOLDER = "trademark_images"

# Ensure output directories exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

# Function to fetch trademark data for a given lodgement date
def fetch_trademark_data(lodgement_date):
    params = {"lodgement_date": lodgement_date}
    
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "items" in data:
                print(f"✅ Found {data['count']} trademarks on {lodgement_date}")
                return data["items"]
            else:
                print(f"⚠️ No 'items' field found in API response for {lodgement_date}.")
                return []
        else:
            print(f"⚠️ Error {response.status_code}: {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Request failed for {lodgement_date}: {e}")
        return []

# Function to download and save images
def download_image(image_url, application_num):
    if not image_url:
        return None  # No image available

    image_filename = f"{application_num}.jpg"
    image_path = os.path.join(IMAGE_FOLDER, image_filename)

    try:
        response = requests.get(image_url, stream=True, timeout=10)
        
        if response.status_code == 200:
            with open(image_path, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)
            print(f"🖼️ Image saved: {image_path}")
            return image_filename  # Save filename for CSV
        else:
            print(f"⚠️ Failed to download image: {image_url}")
            return None
    except Exception as e:
        print(f"⚠️ Error downloading image: {e}")
        return None

# Function to extract relevant fields from API response
def process_trademark_data(records):
    extracted_data = []

    for record in records:
        try:
            summary = record.get("summary", {})
            mark_index = record.get("markIndex", [{}])[0]  # First item in list
            applicant = record.get("currentApplicantProprietorDetails", [{}])[0]
            goods_services_list = record.get("goodsAndServicesSpecifications", [{}])
            documents = record.get("documents", [{}])

            # Get image URL and download image
            image_url = documents[0].get("url")
            application_num = summary.get("applicationNum")
            image_filename = download_image(image_url, application_num)

            # Extract data and store it
            extracted_data.append({
                "Application Number": application_num,
                "Filing Date": summary.get("filingDate"),
                "Mark Name": mark_index.get("wordsInMark"),
                "Trademark Description": summary.get("descriptionParticularFeatureOfMark"),
                "Goods and Services": "; ".join(
                    [item.get("goodsServices", "") for item in goods_services_list]
                ),
                "Applicant Name": applicant.get("name"),
                "Applicant Country": applicant.get("countryOfIncorporationOrResidence", {}).get("description"),
                "Trademark Image URL": image_url,
                "Saved Image File": image_filename,  # Save filename instead of URL
                "Status": summary.get("markStatus"),
                "Expiry Date": summary.get("expiryDate")
            })
        
        except Exception as e:
            print(f"⚠️ Error processing record: {e}")

    return extracted_data

# Function to save data to CSV (append mode)
def save_to_csv(data, filename=CSV_FILE):
    if data:
        df = pd.DataFrame(data)

        # Append to existing CSV if it exists
        if os.path.exists(filename):
            df.to_csv(filename, mode="a", header=False, index=False, encoding="utf-8")
        else:
            df.to_csv(filename, index=False, encoding="utf-8")

        print(f"📁 Data saved to {filename}")
    else:
        print("⚠️ No data to save.")

# Iterate over all dates from 2015 to 2024
start_date = datetime(2015, 1, 1)
end_date = datetime(2024, 12, 31)
current_date = start_date

while current_date <= end_date:
    lodgement_date = current_date.strftime("%Y-%m-%d")  # Convert date to YYYY-MM-DD format
    records = fetch_trademark_data(lodgement_date)

    if records:
        processed_data = process_trademark_data(records)
        save_to_csv(processed_data)

    # Move to the next day
    current_date += timedelta(days=1)
