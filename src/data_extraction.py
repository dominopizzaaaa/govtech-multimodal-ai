import requests
import json
import os
import pandas as pd

# API Endpoint
API_URL = "https://api.data.gov.sg/v1/technology/ipos/trademarks"

# Create a folder for images if it doesn't exist
IMAGE_FOLDER = "trademark_images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Function to fetch trademark data for a given date
def fetch_trademark_data(lodgement_date="2018-01-02"):
    params = {"lodgement_date": lodgement_date}
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        print("🔍 Full API Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        if "items" in data:
            print(f"✅ Found {data['count']} trademarks on {lodgement_date}")
            return data["items"]
        else:
            print(f"⚠️ No 'items' field found in API response for {lodgement_date}.")
            return []
    else:
        print(f"⚠️ Error {response.status_code}: {response.text}")
        return []

# Function to download and save images
def download_image(image_url, application_num):
    if not image_url:
        return None  # No image available

    image_filename = f"{application_num}.jpg"  # Naming images by application number
    image_path = os.path.join(IMAGE_FOLDER, image_filename)

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_path, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)
            print(f"🖼️ Image saved: {image_path}")
            return image_filename  # Return the filename for CSV storage
        else:
            print(f"⚠️ Failed to download image: {image_url}")
            return None
    except Exception as e:
        print(f"⚠️ Error downloading image: {e}")
        return None

# Function to extract useful fields
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
            image_filename = download_image(image_url, application_num)  # Save image

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

# Function to save extracted data to CSV
def save_to_csv(data, filename="trademark_extracted_data.csv"):
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding="utf-8")
        print(f"📁 Data saved to {filename}")
    else:
        print("⚠️ No data to save.")

# Run script for a specific date
if __name__ == "__main__":
    date_to_fetch = "2018-01-02"  # Change as needed
    records = fetch_trademark_data(date_to_fetch)
    processed_data = process_trademark_data(records)
    save_to_csv(processed_data)
