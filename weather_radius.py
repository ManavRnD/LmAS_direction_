import sqlite3
import requests
from cloud_check import cloud_check


def weather_radius(mac_id_data):
    api_error = 0
    direction = []
    locations = []
    distance_weather_id_data = []
    distance_weather_condition_data = []
    found_two_results = False
    count = 0

    try:
        with sqlite3.connect("data(3).sqlite") as connection:
            connection.enable_load_extension(True)
            cursor=connection.cursor()
            cursor.execute(
                "SELECT latitude, longitude, north_latitude, north_longitude, south_latitude, south_longitude, "
                "east_latitude, east_longitude, west_latitude, west_longitude, south_east_latitude, "
                "south_east_longitude, south_west_latitude, south_west_longitude, north_east_latitude, "
                "north_east_longitude, north_west_latitude, north_west_longitude FROM client_db WHERE mac_id=?",
                (mac_id_data,))
            row = cursor.fetchall()


    except Exception as e:

        # Handle the error here, you can print the error message or log it
        print(f"Error: {e}")
        return "Error", str(e)
        # Indicate failure to the caller
