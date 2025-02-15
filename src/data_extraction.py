import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# API Endpoint
API_URL = "https://api.data.gov.sg/v1/technology/ipos/trademarks"

# Year to process (CHANGE THIS FOR EACH RUN)
YEAR_TO_FETCH = 2004  # Set the year you want to process

# Ensure data directory exists
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# CSV file for this year
CSV_FILE = os.path.join(DATA_FOLDER, f"trademark_{YEAR_TO_FETCH}.csv")

# Create a requests session for efficiency
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

# Function to save data to CSV (append mode without duplicates)
def save_to_csv(data):
    if data:
        df = pd.DataFrame(data)

        # Append to existing CSV if it exists
        if os.path.exists(CSV_FILE):
            existing_df = pd.read_csv(CSV_FILE, dtype=str).fillna("")
            combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=["Application Number"])
            combined_df.to_csv(CSV_FILE, index=False, encoding="utf-8")
        else:
            df.to_csv(CSV_FILE, index=False, encoding="utf-8")

        print(f"📁 Data saved to {CSV_FILE}")
    else:
        print("⚠️ No data to save.")

# **Parallel Execution for Faster Processing**
def fetch_and_process_date(lodgement_date):
    """ Fetch data for a single date, process it, and return extracted records. """
    records = fetch_trademark_data(lodgement_date)
    if records:
        return process_trademark_data(records)
    return []

# **Main Execution - Fetch Data for the Selected Year**
if __name__ == "__main__":
    print(f"\n🚀 Fetching data for {YEAR_TO_FETCH}...")

    # Generate all dates for the selected year
    start_date = datetime(YEAR_TO_FETCH, 1, 1)
    end_date = datetime(YEAR_TO_FETCH, 12, 31)
    all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    # Use ThreadPoolExecutor to fetch multiple days in parallel
    batch_size = 20  # Number of dates to process in parallel
    all_data = []

    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        future_to_date = {executor.submit(fetch_and_process_date, date.strftime("%Y-%m-%d")): date for date in all_dates}

        for future in as_completed(future_to_date):
            data = future.result()
            if data:
                all_data.extend(data)

    # Save all collected data for the year
    save_to_csv(all_data)

    print(f"\n✅ Data collection for {YEAR_TO_FETCH} completed successfully!")
