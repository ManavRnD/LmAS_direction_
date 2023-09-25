import asyncio
from flask import Flask, request, jsonify
import aiohttp
from math import radians, degrees, sin, cos

from cloud_check import cloud_check

app = Flask(__name__)


BASE_URL = "http://api.openweathermap.org/data/2.5/"
Apikey='350ce365561bfae47cbfc3ca2f5f59d3'


async def fetch_weather(session, url):
    async with session.get(url) as response:
        data = await response.json()
        return data


async def weather_api(lat,lon, daiac_sat, As):


    lat = lat
    lon = lon


    daiac_sat = int(daiac_sat)
    As = int(As)

    async with aiohttp.ClientSession() as session:
        icon = await fetch_weather(session, f"{BASE_URL}weather?lat={lat}&lon={lon}&appid={Apikey}")
        main_description = icon['weather'][0]['id']
        print('main',main_description)
        hoot= cloud_check(main_description)
        print('hoot',hoot)



        if hoot == 0:
            cloud_conditions = await fetch_weather(session, f"{BASE_URL}onecall?lat={lat}&lon={lon}&appid={Apikey}")
            cloud_data= cloud_conditions['hourly'][1]['weather'][0]['id']
            hoot=cloud_check(cloud_data)
            print('hoot is 0',hoot)
            # Add API calls for distances in different directions


            if hoot==0:
                directions_data = {
                    'north': {'lat': north_lat, 'lon': north_lon},
                    'south': {'lat': south_lat, 'lon': south_lon},
                    'east': {'lat': east_lat, 'lon': east_lon},
                    'west': {'lat': west_lat, 'lon': west_lon},
                    'south_west': {'lat': south_west_lat, 'lon': south_west_lon},
                    'south_east': {'lat': south_east_lat, 'lon': south_east_lon},
                    'north_west': {'lat': north_west_lat, 'lon': north_west_lon},
                    'north_east': {'lat': north_east_lat, 'lon': north_east_lon}
                }

                weather_data_at_distances = []
                main_descriptions = []
                found_two_results = False
                count = 0
                for direction, data in directions_data.items():

                    new_lat = data['lat']
                    new_lon = data['lon']

                    # Make an API call for the new coordinates
                    weather_at_distance = await fetch_weather(session,
                                                              f"{BASE_URL}weather?lat={new_lat}&lon={new_lon}&appid={Apikey}")

                    main_description_at_distance = weather_at_distance['weather'][0]['id']
                    # print('main_descriptioin',main_description_at_distance)
                    cloud_check_result = cloud_check(main_description_at_distance)
                    main_descriptions.append(cloud_check_result)
                    # print('main descrption', main_descriptions)
                    # print('main description', cloud_check_result)
                    if cloud_check_result == 1:
                        count += 1
                        if count == 2:
                            found_two_results = True
                            break

                result = 1 if found_two_results else 0
                # print('Result:', result)
                # Process and store the weather data at this distance
                weather_data_at_distances.append({

                    "cloud_check_result": count >= 2
                })

            return jsonify({
                "Next_hour_data": hoot,

            })

        else:
            return jsonify(hoot)

        # Process the weather data and perform further actions as needed
        # You can extract relevant data from 'icon' and 'cloud_conditions'

        # lmas_result = lmas_result_db(cloud_conditions, clientName, lat, lon, daiac_sat, As)




@app.route('/weatherapi', methods=['GET'])
def weatherapi():
    lat = request.args.get('lat')
    lon=request.args.get('lon')
    daiac_sat = request.args.get('diagsat')
    As = request.args.get('As')

    # Run the asynchronous weather_api function
    result = asyncio.run(weather_api(lat,lon, daiac_sat, As))

    return result


if __name__ == "__main__":
    app.debug = True
    app.run()