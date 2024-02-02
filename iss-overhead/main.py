import os
from dotenv import load_dotenv
import requests
import datetime as dt

load_dotenv()

MY_COORDS = {'lat': os.environ.get("LAT"), 'lon': os.environ.get("LON")}
MY_TZ = os.environ.get("TZID")
EMAIL = os.environ.get("EMAIL")

def get_iss_data():
    ISS_NOW_API = "http://api.open-notify.org/iss-now.json"
    iss_response = requests.get(ISS_NOW_API)
    data = iss_response.json()
    iss_position = data['iss_position']

    return {
        'lat': float(iss_position['latitude']),
        'lon': float(iss_position['longitude'])
    }


def get_sun_data(lat, lng, tz):
    SUNSET_API = "https://api.sunrise-sunset.org/json"
    params = {
        'lat': lat,
        'lng': lng,
        'formatted': 0,
        'tzid': tz
    }
    sunset_response = requests.get(f"{SUNSET_API}", params=params)
    sunset_data = sunset_response.json()['results']

    return {
        'sunrise_time': sunset_data['sunrise'],
        'sunset_time': sunset_data['sunset']
    }


def is_night(lat, lng, tz):
    sunrise_time = get_sun_data(lat, lng, tz)['sunrise_time'] 
    sunset_time = get_sun_data(lat, lng, tz)['sunset_time']
    sunrise_hour = dt.datetime.fromisoformat(sunrise_time).hour
    sunset_hour = dt.datetime.fromisoformat(sunset_time).hour
    hour_now = dt.datetime.now().hour
    return hour_now < sunrise_hour or hour_now > sunset_hour


def send_emai(to_addr, subject, body):
    import smtplib

    app_password = os.environ.get("APP_PASSWORD")
    service_email = os.environ.get("SERVICE_EMAIL")

    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=service_email, password=app_password)
        connection.sendmail(
            from_addr=service_email, 
            to_addrs=to_addr, 
            msg=f"Subject:{subject}\n\n{body}"
        )


lat = float(MY_COORDS['lat']) 
lng = float(MY_COORDS['lon'])

print(f"Is night: {is_night(lat, lng, MY_TZ)}")

def iss_overhead():
    iss_data = get_iss_data()
    iss_lat = float(iss_data['lat'])
    iss_lng = float(iss_data['lon'])
    return (iss_lat > lat - 5 and iss_lat < lat + 5) and (iss_lng > lng - 5 and iss_lng < lng + 5)

iss_data = get_iss_data()
print(f"ISS lat/lon: {iss_data['lat']}, {iss_data['lon']}")

if iss_overhead():
    print("ISS is overhead.")
    body = f"ISS data: {get_iss_data()}"
    send_emai(EMAIL, "ISS is overhead", body)
