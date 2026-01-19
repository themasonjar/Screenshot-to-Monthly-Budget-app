import requests
import json
import pandas as pd
import os

BASE_URL = 'http://localhost:5000/api'

def test_health():
    print("Testing Health Check...")
    try:
        response = requests.get(f'{BASE_URL}/health')
        data = response.json()
        if data['success'] and data['openai_configured']:
            print("✅ Health check passed. OpenAI API key is configured.")
        else:
            print("❌ Health check failed or OpenAI key not configured.")
            print(data)
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")

def create_test_files():
    # JSON
    data = {
        "transactions": [
            {"date": "2023-01-01", "amount": 100.0, "description": "Test Income", "type": "Income"},
            {"date": "2023-01-02", "amount": 50.0, "description": "Test Expense", "type": "Expenses"}
        ]
    }
    with open('test.json', 'w') as f:
        json.dump(data, f)
    
    # CSV
    df_csv = pd.DataFrame([
        {"date": "2023-01-03", "amount": 200.0, "description": "CSV Income"},
        {"date": "2023-01-04", "amount": -20.0, "description": "CSV Expense"}
    ])
    df_csv.to_csv('test.csv', index=False)

    # Excel
    df_excel = pd.DataFrame([
        {"date": "2023-01-05", "amount": 300.0, "description": "Excel Income"},
        {"date": "2023-01-06", "amount": -30.0, "description": "Excel Expense"}
    ])
    df_excel.to_excel('test.xlsx', index=False)

def test_upload_json():
    print("\nTesting JSON Upload...")
    files = {'file': open('test.json', 'rb')}
    data = {'fileType': 'json'}
    try:
        response = requests.post(f'{BASE_URL}/extract-data', files=files, data=data)
        if response.status_code == 200:
            print("✅ JSON upload successful.")
            print(response.json()['data'])
        else:
            print(f"❌ JSON upload failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_upload_csv():
    print("\nTesting CSV Upload (Mocking OpenAI)...")
    # Note: This will actually call OpenAI if key is valid. 
    # If we want to avoid cost/latency we might need to mock, but user asked to test API key.
    files = {'file': open('test.csv', 'rb')}
    data = {'fileType': 'csv'}
    try:
        response = requests.post(f'{BASE_URL}/extract-data', files=files, data=data)
        if response.status_code == 200:
            print("✅ CSV upload successful.")
            # print(response.json()['data']) # Output might be large
        else:
            print(f"❌ CSV upload failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_upload_excel():
    print("\nTesting Excel Upload (Mocking OpenAI)...")
    files = {'file': open('test.xlsx', 'rb')}
    data = {'fileType': 'excel'}
    try:
        response = requests.post(f'{BASE_URL}/extract-data', files=files, data=data)
        if response.status_code == 200:
            print("✅ Excel upload successful.")
        else:
            print(f"❌ Excel upload failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_health()
    create_test_files()
    test_upload_json()
    test_upload_csv() 
    test_upload_excel()
    
    # Clean up
    if os.path.exists('test.json'): os.remove('test.json')
    if os.path.exists('test.csv'): os.remove('test.csv')
    if os.path.exists('test.xlsx'): os.remove('test.xlsx')
