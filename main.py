from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from data_manager import data_manager

app = FastAPI(title="Global Energy Consumption API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/countries")
async def get_countries():
    return data_manager.get_countries()

@app.get("/api/trends")
async def get_trends(country: str = Query(..., description="Country name")):
    return data_manager.get_trends(country)

@app.get("/api/energy-types")
async def get_energy_mix(country: str = Query(...), year: int = Query(...)):
    return data_manager.get_energy_mix(country, year)

@app.get("/api/map-data")
async def get_map_data(year: int = Query(...)):
    return data_manager.get_map_data(year)

@app.get("/api/insights")
async def get_insights():
    return data_manager.get_insights()

@app.get("/api/compare-trends")
async def get_compare_trends(countries: list[str] = Query(...)):
    return data_manager.get_comparison_trends(countries)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
