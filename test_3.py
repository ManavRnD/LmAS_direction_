## shahin code

import sqlite3
import requests
from cloud_check import cloud_check
from config import weather_api
from email_system import send_email_alert


def get_distance_weather(mac_id_data, apikey_data):
    api_error = 0
    direction = []
    locations = []
    distance_weather_id_data = []
    distance_weather_condition_data = []
    found_two_results = False
    count = 0

    try:
        with sqlite3.connect("instance/lmas-database.sqlite") as connection:
            connection.enable_load_extension(True)
            cursor = connection.cursor()
            cursor.execute(
                "SELECT latitude, longitude, north_latitude, north_longitude, south_latitude, south_longitude, "
                "east_latitude, east_longitude, west_latitude, west_longitude, south_east_latitude, "
                "south_east_longitude, south_west_latitude, south_west_longitude, north_east_latitude, "
                "north_east_longitude, north_west_latitude, north_west_longitude FROM client_db WHERE mac_id=?",
                (mac_id_data,))
            row = cursor.fetchall()

            print("distance-row", row)

            direction.append(row[0])
            print("direction-append", direction)

            north_lat = direction[0][2]
            north_lon = direction[0][3]
            south_lat = direction[0][4]
            south_lon = direction[0][5]
            east_lat = direction[0][6]
            east_lon = direction[0][7]
            west_lat = direction[0][8]
            west_lon = direction[0][9]
            south_east_lat = direction[0][10]
            south_east_lon = direction[0][11]
            south_west_lat = direction[0][12]
            south_west_lon = direction[0][13]
            north_east_lat = direction[0][14]
            north_east_lon = direction[0][15]
            north_west_lat = direction[0][16]
            north_west_lon = direction[0][17]

            # Create the directions list
            directions_data = {
                'North': {'lat': north_lat, 'lon': north_lon, 'direction': 'North'},
                'South': {'lat': south_lat, 'lon': south_lon, 'direction': 'South'},
                'East': {'lat': east_lat, 'lon': east_lon, 'direction': 'East'},
                'West': {'lat': west_lat, 'lon': west_lon, 'direction': 'West'},
                'South West': {'lat': south_west_lat, 'lon': south_west_lon, 'direction': 'South West'},
                'South East': {'lat': south_east_lat, 'lon': south_east_lon, 'direction': 'South East'},
                'North West': {'lat': north_west_lat, 'lon': north_west_lon, 'direction': 'North West'},
                'North East': {'lat': north_east_lat, 'lon': north_east_lon, 'direction': 'North East'}
            }

            for direction, data in directions_data.items():

                dir_latitude = data['lat']
                dir_longitude = data['lon']
                locations.append(data['direction'])

                # Make an API call for the new coordinates
                distance_weather_data_url = f"{weather_api}weather?lat={dir_latitude}&lon={dir_longitude}&appid={apikey_data}"
                distance_weather_data = requests.get(distance_weather_data_url).json()

                # print("distance-weather-for", distance_weather_data)

                if distance_weather_data['cod'] == 200:
                    distance_weather_id = distance_weather_data['weather'][0]['id']
                    distance_weather_condition = distance_weather_data['weather'][0]['main']
                    # print('Distance ID', distance_weather_id)

                    cloud_condition = cloud_check(distance_weather_id)
                    distance_weather_id_data.append(distance_weather_id)
                    # print('distance-id-append', distance_weather_id_data)
                    distance_weather_condition_data.append(distance_weather_condition)
                    # print('distance-condition-append', distance_weather_condition_data)
                    # main_descriptions.append(cloud_check_result)
                    #
                    # print('main description', main_descriptions)
                    # print('main description', cloud_condition)
                    if cloud_condition == 1:
                        print("count", count)
                        count += 1
                        print("count+", count)
                        if count == 2:
                            print("count=2", count)
                            found_two_results = True
                            print("two-result", found_two_results)
                            print("api-error", api_error)
                            break
                else:
                    send_email_alert(distance_weather_data)
                    api_error = 1
                    break

            if found_two_results is True:
                cloud_condition = 1
            else:
                cloud_condition = 0

            # print('Result:', result)
            return cloud_condition, locations, count, distance_weather_id_data, distance_weather_condition_data, api_error

    except Exception as e:
        # Handle the error here, you can print the error message or log it
        print(f"Error: {e}")
        return "Error", str(e)
        # Indicate failure to the caller
