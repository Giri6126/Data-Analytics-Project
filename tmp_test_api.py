import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_compare_trends():
    countries = ["United States", "China", "India"]
    params = {"countries": countries}
    try:
        response = requests.get(f"{BASE_URL}/compare-trends", params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Number of years: {len(data)}")
            if data:
                print(f"Sample data for {data[0]['year']}: {data[0]}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_compare_trends()
