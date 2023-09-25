import asyncio
from flask import Flask, request, jsonify
import aiohttp
from math import radians, degrees, sin, cos
from datetime import datetime, timedelta
from Lmas_databse_push import db_push


from cloud_check import cloud_check
import sqlite3
from sqlite3 import Error

app = Flask(__name__)


BASE_URL = "http://api.openweathermap.org/data/2.5/"
Apikey='350ce365561bfae47cbfc3ca2f5f59d3'


async def fetch_weather(session, url):
    async with session.get(url) as response:
        data = await response.json()
        return data


async def weather_api(lat,lon, daiac_sat, As):

    connection=sqlite3.connect("data(3).sqlite")
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM lmas__result_db WHERE name='LMAS-BALCO'")
    rows=cursor.fetchall()
    sorted_rows = sorted(rows, key=lambda x: x[4], reverse=True)
    latest_two_readings = sorted_rows[:2]
    # print('latest readings',latest_two_readings)
    latest_time_and_date = [reading[4] for reading in latest_two_readings]
    CF = [reading[20] for reading in latest_two_readings]
    start_time = [reading[21] for reading in latest_two_readings]
    saved_count = [reading[22] for reading in latest_two_readings]
    print('count',saved_count)
    latest_direction = [reading[19] for reading in latest_two_readings]

    current_time = datetime.now()
    # print('Current time', current_time)
    saved_latest_date=datetime.strptime(latest_time_and_date[0], '%Y-%m-%d %H:%M:%S')

    diacsat=daiac_sat
    As=As
    current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
    current_time_db = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M:%S')

    cf_prev=CF[0]


    lat = lat
    lon = lon




    async with aiohttp.ClientSession() as session:
        icon = await fetch_weather(session, f"{BASE_URL}weather?lat={lat}&lon={lon}&appid={Apikey}")
        main_description = icon['weather'][0]['id']
        # print('main',main_description)
        hoot= cloud_check(main_description)
        # print('hoot',hoot)



        if hoot == 0:
            cloud_conditions = await fetch_weather(session, f"{BASE_URL}onecall?lat={lat}&lon={lon}&appid={Apikey}")
            cloud_data= cloud_conditions['hourly'][1]['weather'][0]['id']
            # print('forecat cloud',cloud_data)
            hoot=cloud_check(cloud_data)
            print('hoot is 0',hoot)

            # Add API calls for distances in different directions

            if hoot == 0:
                continous_flag=cf_prev
                count=saved_count[0]

                saved_start_time = datetime.strptime(start_time[0], '%Y-%m-%d %H:%M:%S')
                if saved_latest_date.date() == current_time.date():
                    time_diffrence = current_time-saved_latest_date
                    twenty_five_minutes = timedelta(minutes=25)
                    if time_diffrence < twenty_five_minutes:
                        if continous_flag == 0:
                            continous_flag= +1
                            if count == 3:
                                print('if cf=0 and count=3 set cf to 1 ')
                                start=current_time_db
                                print('start time to be reset',start)
                                count=2
                                db=db_push(current_time_db,lat,lon,daiac_sat,As,hoot,continous_flag,start,count)
                                return jsonify('start time to be reset, cf-0 and count -3')

                            else:
                                print('Return Count')
                                print('contionous flag set to 1',continous_flag)
                                start=current_time_db
                                count=2
                                db = db_push(current_time_db, lat, lon, daiac_sat, As, hoot, continous_flag, start,count)
                                print('start time to be reset',start)
                                return jsonify(start_time,continous_flag,'start time to be reset, cf-0 and count -0/1/2')
                        else:
                            print('the calls are continous')
                            # assuming 5 is the threshold
                            if continous_flag >= 5:
                                time_diffrence= current_time-saved_start_time
                                print('flag is greater than 5 check time diffrence',time_diffrence)
                                twenty_minutes = timedelta(minutes=4)
                                if time_diffrence >= twenty_minutes:
                                    # print('do a distance call')
                                    continous_flag=0
                                    print('continous flag set to 0',continous_flag)
                                    start=current_time_db
                                    count=3
                                    db = db_push(current_time_db, lat, lon, daiac_sat, As, hoot, continous_flag, start,count)
                                    print('set the start time now as current time')
                                    return jsonify(continous_flag,'reseting cf and start time and did a distance call')
                                else:
                                    continous_flag = continous_flag+1
                                    count=saved_count[0]
                                    db = db_push(current_time_db, lat, lon, daiac_sat, As, hoot, continous_flag,
                                                 start_time[0],count)
                                    print('continous but not more than 20 min since start')
                                    return jsonify('continous but not more than 10 min since start, just increase the CF',continous_flag,count)
                            else:
                                continous_flag = continous_flag + 1
                                count=saved_count[0]
                                db = db_push(current_time_db, lat, lon, daiac_sat, As, hoot, continous_flag, start_time[0],count)
                                print('return count')
                                return jsonify('continous flag, not reached threshold',continous_flag,count)

                    else:
                        continous_flag=0
                        print('Time Diffrence is greater than or eqaul to 25 mins, do a distance call and cet Continous Flag to 0',continous_flag)
                        count = saved_count[0]
                        db = db_push(current_time_db, lat, lon, daiac_sat, As, hoot, continous_flag, start_time[0],
                                     count)
                        return jsonify('Time Diffrence more than 25')
                else:
                    print('Dates are not same do direction call')
                    return jsonify('dates are not same do a direction call')
            else:
                continous_flag = 0
                start_time = current_time_db
                count = 3
                db = db_push(current_time_db, lat, lon, daiac_sat, As, hoot, continous_flag, current_time_db, count)
                return jsonify(hoot)

        else:
            continous_flag=0
            start_time=current_time_db
            count=3
            db = db_push(current_time_db, lat, lon, daiac_sat, As, hoot, continous_flag, current_time_db, count)
            return jsonify(hoot)



        # lmas_result = lmas_result_db(cloud_conditions, clientName, lat, lon, daiac_sat, As)




@app.route('/weatherapi', methods=['GET'])
def weatherapi():
    lat = request.args.get('lat')
    lon=request.args.get('lon')
    daiac_sat = request.args.get('diagsat')
    As = request.args.get('As')
    # timestamp = request.args.get('timestamp')
    # print('lat',lat)
    # print('lon', lon)
    # print('diagsat', daiac_sat)
    # print('As', As)

    # Run the asynchronous weather_api function
    result = asyncio.run(weather_api(lat,lon, daiac_sat, As))

    return result


if __name__ == "__main__":
    app.debug = True
    app.run()