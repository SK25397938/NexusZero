import requests

def check_storm(lat, lng):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=precipitation"
        res = requests.get(url, timeout=3).json()

        rain = max(res.get("hourly", {}).get("precipitation", [0]))
        return rain > 5
    except:
        return False