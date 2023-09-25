from datetime import datetime, timedelta


previous_data=['2023-09-14 11:30:14','2']

p1_data=['2023-09-14 11:02:09','1']

current_time= datetime.now()


saved_latest_date = datetime.strptime(previous_data[0], '%Y-%m-%d %H:%M:%S')
saved_previous_date = datetime.strptime(p1_data[0], '%Y-%m-%d %H:%M:%S')
saved_p_count= previous_data[1]
saved_p1_count= p1_data[1]


if saved_latest_date.date() == current_time.date():
    time_diffrence = current_time - saved_latest_date
    if saved_latest_date.date() == saved_previous_date.date():
        time_between_calls = saved_latest_date - saved_previous_date
        print(time_diffrence)
    else:
        time_between_calls= timedelta(minutes=0)

    print('is it contnious triggering', time_between_calls)
    twenty_five_minutes = timedelta(minutes=25)
    fifty_minutes = timedelta(minutes=50)

    if time_diffrence <= twenty_five_minutes and saved_p_count == '3':
        print('direction call didnt happen before should be done now ')
    elif time_diffrence<= twenty_five_minutes and saved_p_count =='2' or saved_p_count=='1' or saved_p_count=='0':
        time_since_last_call = time_diffrence + time_between_calls
        print('is it continous calling',time_since_last_call)
        if time_since_last_call >= fifty_minutes:
            print('it is not continous yet, do a direction call now')
        else:
            print("return count i.e. hoot")
    else:
        print('its more than 25 mins do a direction call')

else:
    print('date is diffrent do a direction call')