import os
import requests
import pandas as pd
from datetime import datetime, timedelta

# API Endpoint
API_URL = "https://api.data.gov.sg/v1/technology/ipos/trademarks"

# File path
CSV_FILE = "data/trademark_extracted_data.csv"

# Ensure output directory exists
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

            # Extract data fields
            extracted_data.append({
                "Application Number": summary.get("applicationNum", ""),
                "Filing Date": summary.get("filingDate", ""),
                "Mark Name": mark_index.get("wordsInMark", ""),
                "Trademark Description": summary.get("descriptionParticularFeatureOfMark", ""),
                "Goods and Services": "; ".join(
                    [item.get("goodsServices", "") for item in goods_services_list]
                ),
                "Applicant Name": applicant.get("name", ""),
                "Applicant Country": applicant.get("countryOfIncorporationOrResidence", {}).get("description", ""),
                "Trademark Image URL": documents[0].get("url", ""),  # Keep only the image URL
                "Status": summary.get("markStatus", ""),
                "Expiry Date": summary.get("expiryDate", "")
            })
        
        except Exception as e:
            print(f"⚠️ Error processing record: {e}")

    return extracted_data

# Function to save data to CSV (append mode without duplicates)
def save_to_csv(data, filename=CSV_FILE):
    if data:
        df = pd.DataFrame(data)

        # Append to existing CSV if it exists
        if os.path.exists(filename):
            existing_df = pd.read_csv(filename, dtype=str).fillna("")
            combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=["Application Number"])
            combined_df.to_csv(filename, index=False, encoding="utf-8")
        else:
            df.to_csv(filename, index=False, encoding="utf-8")

        print(f"📁 Data saved to {filename}")
    else:
        print("⚠️ No data to save.")

# Iterate over all dates from 2004 to 2024
start_date = datetime(2004, 1, 1)
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
