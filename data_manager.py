import csv
import requests
import os
from collections import defaultdict

DATA_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
LOCAL_FILE = "energy_data.csv"

class DataManager:
    def __init__(self):
        self.data = []
        self.is_loading = True
        # For simplicity in this small project, we'll load synchronously 
        # but add better error handling to avoid 500s.
        self.load_data()

    def load_data(self):
        if not os.path.exists(LOCAL_FILE):
            print("Downloading energy dataset...")
            try:
                response = requests.get(DATA_URL, timeout=10)
                response.raise_for_status()
                with open(LOCAL_FILE, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Error downloading data: {e}")
                self.is_loading = False
                return

        print("Loading data from CSV...")
        try:
            with open(LOCAL_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # Optimization: Only load necessary columns to save memory and time
                needed_cols = {'country', 'year', 'iso_code', 'energy_per_capita', 
                              'renewables_share_energy', 'fossil_share_energy',
                              'fossil_fuel_consumption', 'renewables_consumption',
                              'nuclear_consumption', 'other_renewable_consumption',
                              'primary_energy_consumption'}
                
                rows = []
                for row in reader:
                    try:
                        year = int(row['year'])
                        if year >= 2000: # Only load data since 2000 for "lightweight" version
                            cleaned_row = {'country': row['country'], 'year': year, 'iso_code': row.get('iso_code', '')}
                            for col in needed_cols:
                                if col in row and col not in cleaned_row:
                                    val = row[col]
                                    cleaned_row[col] = float(val) if val else 0
                            rows.append(cleaned_row)
                    except:
                        continue
                self.data = rows
            print(f"Loaded {len(self.data)} records.")
        except Exception as e:
            print(f"Error loading CSV: {e}")
        finally:
            self.is_loading = False

    def get_countries(self):
        if not self.data: return ["Loading data..."]
        countries = set()
        for row in self.data:
            iso = str(row.get('iso_code', ''))
            if iso and not iso.startswith('OWID_'):
                countries.add(row['country'])
        return sorted(list(countries))

    def get_trends(self, country: str):
        result = []
        for row in self.data:
            if row['country'] == country:
                result.append({
                    'year': row['year'],
                    'energy_per_capita': row.get('energy_per_capita', 0),
                    'renewables_share_energy': row.get('renewables_share_energy', 0),
                    'fossil_share_energy': row.get('fossil_share_energy', 0)
                })
        return sorted(result, key=lambda x: x['year'])

    def get_energy_mix(self, country: str, year: int):
        for row in self.data:
            if row['country'] == country and row['year'] == year:
                return {
                    "fossil": row.get('fossil_fuel_consumption', 0),
                    "renewable": row.get('renewables_consumption', 0),
                    "nuclear": row.get('nuclear_consumption', 0),
                    "other": row.get('other_renewable_consumption', 0)
                }
        return {}

    def get_map_data(self, year: int):
        result = []
        for row in self.data:
            iso = str(row.get('iso_code', ''))
            if row['year'] == year and iso:
                result.append({
                    'iso_code': iso,
                    'country': row['country'],
                    'primary_energy_consumption': row.get('primary_energy_consumption', 0)
                })
        return result

    def get_insights(self):
        if not self.data:
            return {}
            
        latest_year = max(row['year'] for row in self.data)
        data_latest = [row for row in self.data if row['year'] == latest_year and str(row.get('iso_code', '')).strip() and not str(row.get('iso_code', '')).startswith('OWID_')]
        
        if not data_latest:
            return {"latest_year": int(latest_year)}

        top_consumer_row = max(data_latest, key=lambda x: x.get('primary_energy_consumption', 0))
        avg_consumption = sum(row.get('primary_energy_consumption', 0) for row in data_latest) / len(data_latest)
        
        return {
            "top_consumer": top_consumer_row['country'],
            "latest_year": int(latest_year),
            "global_avg_consumption": float(avg_consumption)
        }

    def get_comparison_trends(self, countries: list[str]):
        # Data structure for Recharts: [{"year": 2000, "Country1": val, "Country2": val}, ...]
        yearly_data = defaultdict(lambda: {"year": 0})
        
        for row in self.data:
            country = row['country']
            if country in countries:
                year = row['year']
                yearly_data[year]["year"] = year
                yearly_data[year][country] = row.get('primary_energy_consumption', 0)
        
        # Sort by year and return as list
        return sorted(list(yearly_data.values()), key=lambda x: x['year'])

data_manager = DataManager()
