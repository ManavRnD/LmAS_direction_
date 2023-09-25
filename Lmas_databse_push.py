import sqlite3


def db_push(date_time,lat,lon,diacsat,AS3935,hoot,cf,start_time,count):
    connection = sqlite3.connect("data(3).sqlite")
    cursor = connection.cursor()
    name='LMAS-BALCO'
    cloud_conditions=hoot
    main=199
    forecast='NA'
    forecast_description= 'NA'
    main_description="NA"
    weightage= 85
    temperature=22
    pressure=12
    humidity=12
    email='test'
    status='True'
    directions='NA'
    print('start time',start_time)




    cursor.execute(
        "INSERT INTO lmas__result_db (name,date_time,lat, lon, diacsat, AS3935,"
        "cloud_conditions,hoot,main, main_description,forecast,forecast_description,weightage,temperature,pressure,humidity,email,status,directions,cf,start_time,count) VALUES (?,?,?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (name,date_time,lat,lon,diacsat,AS3935,cloud_conditions,hoot,main,main_description,forecast,forecast_description,weightage,temperature,pressure,humidity,email,status,directions,cf,start_time,count))

    connection.commit()
    connection.close()

    return "success"
