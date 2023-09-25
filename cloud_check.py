def cloud_check(weather_data):
    true = 1
    false = 0

    # print("cloud-check")

    if weather_data == 800:
        return false
    # thunderstorm
    elif 232 >= weather_data >= 200:
        return true
    # rain
    elif 511 >= weather_data >= 500:
        return true
    # drizzle
    elif 321 >= weather_data >= 300:
        return true
    # shower rain
    elif 531 >= weather_data >= 520:
        return true
    # tornado
    elif weather_data == 781:
        return true
    # snow
    elif 622 >= weather_data >= 600:
        return true

    else:
        return false