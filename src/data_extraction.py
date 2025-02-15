import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# API Endpoint
API_URL = "https://api.data.gov.sg/v1/technology/ipos/trademarks"

# Output directory
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# Create a persistent HTTP session
session = requests.Session()

# Function to fetch trademark data for a given lodgement date
def fetch_trademark_data(lodgement_date):
    params = {"lodgement_date": lodgement_date}
    
    try:
        response = session.get(API_URL, params=params, timeout=10)
        
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

# Function to save data to a year-specific CSV file
def save_to_csv(data, year):
    filename = os.path.join(DATA_FOLDER, f"trademark_{year}.csv")

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
        print(f"⚠️ No data to save for {year}.")

# Function to process an entire year using multi-threading
def process_year(year):
    print(f"\n🚀 Processing trademarks for the year {year}...\n")
    
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    all_data = []
    
    # Use threading to fetch multiple days in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
        future_to_date = {executor.submit(fetch_trademark_data, (start_date + timedelta(days=i)).strftime("%Y-%m-%d")): i for i in range((end_date - start_date).days + 1)}
        
        for future in as_completed(future_to_date):
            records = future.result()
            if records:
                all_data.extend(process_trademark_data(records))

    # Save data for the year
    save_to_csv(all_data, year)

# Loop through each year from 2004 to 2024
for year in range(2004, 2025):
    process_year(year)

print("\n✅ Data extraction completed for all years from 2004 to 2024!")
