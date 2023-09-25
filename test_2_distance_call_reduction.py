## shahin code



import sqlite3

import aiohttp
from cloud_check import cloud_check
from config import weather_api
from distance_weather import get_distance_weather
from email_system import send_email_alert
from forecast_data_check import forecast_data_check
from weather_db_save import weather_data_db
from datetime import datetime, timedelta


async def fetch_weather(session, url):
    async with session.get(url) as response:
        data = await response.json()
        return data


async def weather_api_async(latitude_data, longitude_data, diagsat_data, AS3935_data, mac_id_data, apikey_data):
    latitude = latitude_data
    longitude = longitude_data

    diagsat = int(diagsat_data)
    AS3935 = int(AS3935_data)

    async with aiohttp.ClientSession() as session:
        weather_data = await fetch_weather(session,
                                           f"{weather_api}weather?lat={latitude}&lon={longitude}&appid={apikey_data}")
        # print('weather-data', weather_data)

        if weather_data['cod'] == 200:
            weather_data_save = weather_data_db(weather_data, mac_id_data, diagsat, AS3935)

            weather_condition = weather_data['weather'][0]['main']
            weather_condition_id = weather_data['weather'][0]['id']
            temperature_id = weather_data['main']['temp']
            pressure_id = weather_data['main']['pressure']
            humidity_id = weather_data['main']['humidity']
            forecast_condition = 'NA'
            forecast_condition_id = 'NA'
            locations = 'NA'
            distance_weather_id_data = 'NA'
            distance_weather_condition_data = 'NA'

            # print('weather_data_save', weather_data_save)

            cloud_condition = cloud_check(weather_condition_id)
            count = 3
            print('hoot weather', cloud_condition)

            if cloud_condition == 0:
                try:
                    forecast_data = await fetch_weather(session,
                                                        f"{weather_api}onecall?lat={latitude}&lon={longitude}&appid={apikey_data}")

                    print("forcast_db", forecast_data)

                    forecast_check = forecast_data_check(forecast_data)
                    forecast_condition = forecast_check[0]
                    forecast_condition_id = forecast_check[1]

                    print("forcast_id", forecast_condition_id)

                    cloud_condition = cloud_check(forecast_condition_id)
                    print('hoot forecast', cloud_condition)

                    # Add API calls for distances in different directions
                    if cloud_condition == 0:
                        print('in distance loop')
                        with sqlite3.connect("instance/lmas-database.sqlite") as connection:
                            connection.enable_load_extension(True)
                            cursor = connection.cursor()
                            # Fetch the latest two rows
                            cursor.execute(
                                "SELECT date_time, count FROM lmas_result_db ORDER BY id DESC LIMIT 2")
                            latest_data = cursor.fetchall()

                            print("distance-count-data", latest_data)

                            if len(latest_data) == 2:
                                data_1 = latest_data[0]
                                data_2 = latest_data[1]

                                current_time = datetime.now()
                                # current_time = new_time.strftime("%H:%M:%S")
                                print("curr-time", current_time)

                                saved_latest_date = datetime.strptime(data_1[0], '%Y-%m-%d %H:%M:%S')
                                saved_previous_date = datetime.strptime(data_2[0], '%Y-%m-%d %H:%M:%S')
                                saved_latest_count = data_1[1]
                                saved_previous_count = data_2[1]
                                print('count1', saved_latest_count)
                                print('count2', saved_previous_count)

                                if saved_latest_date.date() == current_time.date():

                                    time_difference = current_time - saved_latest_date
                                    print("time difference", time_difference)
                                    if saved_latest_date.date() == saved_previous_date.date():
                                        time_between_calls = saved_latest_date - saved_previous_date
                                        print("time-between-calls-saved-calls", time_between_calls)
                                    else:
                                        time_between_calls = timedelta(minutes=0)
                                        print("timedelta", time_between_calls)

                                    print('IS it contnious triggering', time_between_calls)
                                    twenty_five_minutes = timedelta(minutes=25)
                                    print('25 min', twenty_five_minutes)
                                    fifty_minutes = timedelta(minutes=50)
                                    print('50 min', fifty_minutes)
                                    print('count', saved_latest_count)

                                    if time_difference <= twenty_five_minutes and saved_latest_count == '3':

                                        time_since_last_call = time_difference + time_between_calls

                                        print('direction call didnt happen before should be done now ')
                                        distance_data = get_distance_weather(mac_id_data, apikey_data)
                                        if distance_data[5] == 0:
                                            cloud_condition = distance_data[0]
                                            locations = distance_data[1]
                                            count = distance_data[2]
                                            distance_weather_id_data = distance_data[3]
                                            distance_weather_condition_data = distance_data[4]

                                            return cloud_condition, weather_condition, weather_condition_id, temperature_id, \
                                                   pressure_id, humidity_id, forecast_condition, forecast_condition_id, \
                                                   locations, count, distance_weather_id_data, \
                                                   distance_weather_condition_data

                                        else:
                                            return "Error"

                                    elif time_difference <= twenty_five_minutes and (saved_latest_count == '2' or
                                                                                     saved_latest_count == '1' or
                                                                                     saved_latest_count == '0'):

                                        time_since_last_call = time_difference + time_between_calls
                                        print('is it continuous calling-elif-statement', time_since_last_call)

                                        if time_since_last_call >= fifty_minutes:
                                            print('it is not continuous yet, do a direction call now')
                                            distance_data = get_distance_weather(mac_id_data, apikey_data)

                                            if distance_data[5] == 0:
                                                cloud_condition = distance_data[0]
                                                locations = distance_data[1]
                                                count = distance_data[2]
                                                distance_weather_id_data = distance_data[3]
                                                distance_weather_condition_data = distance_data[4]

                                                return cloud_condition, weather_condition, weather_condition_id, \
                                                       temperature_id, pressure_id, humidity_id, forecast_condition, \
                                                       forecast_condition_id, locations, count, distance_weather_id_data, \
                                                       distance_weather_condition_data
                                            else:
                                                return "Error"

                                        else:
                                            print("return count i.e. hoot")
                                            count = saved_latest_count
                                            return cloud_condition, weather_condition, weather_condition_id, \
                                                   temperature_id, pressure_id, humidity_id, forecast_condition, \
                                                   forecast_condition_id, locations, count, distance_weather_id_data, \
                                                   distance_weather_condition_data

                                    else:
                                        print('its more than 25 minutes do a direction call')
                                        distance_data = get_distance_weather(mac_id_data, apikey_data)

                                        if distance_data[5] == 0:
                                            cloud_condition = distance_data[0]
                                            locations = distance_data[1]
                                            count = distance_data[2]
                                            distance_weather_id_data = distance_data[3]
                                            distance_weather_condition_data = distance_data[4]

                                            return cloud_condition, weather_condition, weather_condition_id, temperature_id, \
                                                   pressure_id, humidity_id, forecast_condition, forecast_condition_id, \
                                                   locations, count, distance_weather_id_data, \
                                                   distance_weather_condition_data
                                        else:
                                            return "Error"

                                else:
                                    print('date is different do a direction call')
                                    distance_data = get_distance_weather(mac_id_data, apikey_data)

                                    cloud_condition = distance_data[0]
                                    locations = distance_data[1]
                                    count = distance_data[2]
                                    distance_weather_id_data = distance_data[3]
                                    distance_weather_condition_data = distance_data[4]

                                    return cloud_condition, weather_condition, weather_condition_id, temperature_id, \
                                           pressure_id, humidity_id, forecast_condition, forecast_condition_id, \
                                           locations, count, distance_weather_id_data, distance_weather_condition_data

                            else:
                                print('No Rows added yet distance call')
                                distance_data = get_distance_weather(mac_id_data, apikey_data)

                                cloud_condition = distance_data[0]
                                locations = distance_data[1]
                                count = distance_data[2]
                                distance_weather_id_data = distance_data[3]
                                distance_weather_condition_data = distance_data[4]

                                return cloud_condition, weather_condition, weather_condition_id, temperature_id, \
                                       pressure_id, humidity_id, forecast_condition, forecast_condition_id, \
                                       locations, count, distance_weather_id_data, distance_weather_condition_data

                    else:
                        return cloud_condition, weather_condition, weather_condition_id, temperature_id, pressure_id, \
                               humidity_id, forecast_condition, forecast_condition_id, locations, count, \
                               distance_weather_id_data, distance_weather_condition_data

                except Exception as e:
                    # Handle the error here, you can print the error message or log it
                    print(f"Error: {e}")
                    return "Error", e  # Indicate failure to the caller

            else:
                return cloud_condition, weather_condition, weather_condition_id, temperature_id, pressure_id, \
                       humidity_id, forecast_condition, forecast_condition_id, locations, count, \
                       distance_weather_id_data, distance_weather_condition_data

        else:
            send_email_alert(weather_data)
            return "Error"
