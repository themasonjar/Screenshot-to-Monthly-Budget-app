import requests
import pandas as pd
import os
import time

BASE_URL = 'http://localhost:5000/api'

def create_large_csv(filename='large_test.csv', rows=120):
    print(f"Generating {rows} rows CSV...")
    data = []
    for i in range(rows):
        data.append({
            "date": "2023-01-01",
            "amount": float(i + 10),
            "description": f"Transaction number {i}"
        })
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Created {filename}")

def test_chunking():
    create_large_csv()
    
    print("\nUploading large CSV (expecting chunked processing)...")
    start_time = time.time()
    
    try:
        with open('large_test.csv', 'rb') as f:
            files = {'file': f}
            data = {'fileType': 'csv'}
            response = requests.post(f'{BASE_URL}/extract-data', files=files, data=data)
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            extracted_count = len(result['data'])
            print(f"✅ Success! Extracted {extracted_count} transactions in {duration:.2f}s")
            
            # Verify we got close to 120 (AI might drop/merge some, but should be > 100)
            if extracted_count > 100:
                print("   Length verification passed.")
            else:
                print(f"   ⚠️ Warning: Only extracted {extracted_count} rows (expected ~120).")
        else:
            print(f"❌ Failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if os.path.exists('large_test.csv'):
            os.remove('large_test.csv')

if __name__ == "__main__":
    test_chunking()
