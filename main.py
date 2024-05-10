
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from fastapi import FastAPI, Form, UploadFile, File, Request, Response, HTTPException,Depends
import mysql.connector
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback
import re
import bcrypt
import hashlib
import paho.mqtt.client as mqtt
from passlib.hash import bcrypt
from cachetools import LRUCache
import threading
from datetime import datetime, timedelta
from typing import List, Dict
import calendar


app = FastAPI()
cache = LRUCache(maxsize=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mysql_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'electrivity_server'
}

mqtt_clients={}

connection = mysql.connector.connect(**mysql_config)
print(connection)


SECRET_KEY = "your-secret-key"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "fawdmuhammad14@gmail.com"
SMTP_PASSWORD = "vxzxanmeiemaougl"
client = None

@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.post("/register")
async def register(email: str = Form(...), username: str = Form(...),password: str = Form(...), confirmpassword: str = Form(...)):
    try:
        # print("Received form data:")
        # print("Email:", email)
        # print("Username:", username)
        # print("Password:", password)
        # print("Confirm Password:", confirmpassword)
        if not email or not username or not password or not confirmpassword:
            return JSONResponse(content={'error': "Missing Fields"}, status_code=422)

        if not validate_email(email):
            return JSONResponse(content={'error': "Please Enter Correct Email"}, status_code=422)

        if len(password) < 8:
            return JSONResponse(content={'error': "Password length should be more than 8"}, status_code=422)

        if password != confirmpassword:
            return JSONResponse(content={'error': "Password not matched"}, status_code=422)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_exists = cursor.fetchone()
        cursor.close()
        if user_exists:
            return JSONResponse(content={'error': "User already exists"}, status_code=500)
        
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", (email, username, hashed_password))
        connection.commit()
        cursor.close()

        return JSONResponse(content={'message': "Successfully Registered"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)
def validate_email(email):
    email_regex = r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
    return bool(re.match(email_regex, email, re.IGNORECASE))


@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
        # print("Email:", email)
        # print("Password:", password)
        if not email or not password:
            return JSONResponse(content={'error': "Missing Fields"}, status_code=422)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return JSONResponse(content={'error': "Invalid username or password"}, status_code=401)

        stored_password_hash = user[3]
        input_password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        if input_password_hash == stored_password_hash:
            return JSONResponse(content={'user_id': user[0], 'username': user[2]}, status_code=200)
        else:
            return JSONResponse(content={'error': "Password not matched"}, status_code=401)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)


def connect_to_mqtt(user_id, ipAddress, port):

    mqtt_clients[user_id] = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    print(mqtt_clients)
    mqtt_clients[user_id].connect(ipAddress, port, 60)
    mqtt_clients[user_id].loop_start()
    print(f"{user_id} connected to {ipAddress} on port no. {port}")

# //////////////////////////////////////////////////////////////////////////////////////////////////
@app.post("/resetemail")
async def reset_email(email: str = Form(...)):
    try:
        # print("Email:", email)
        cursor = connection.cursor()
        cursor.execute("SELECT id, email, username FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        # print("User:", user)
        cursor.close()
        if not user:
            return JSONResponse(content={'error': "Password not matched"}, status_code=404)

        cursor = connection.cursor()
        cursor.execute("SELECT otp FROM otps WHERE email = %s", (email,))
        existing_otp = cursor.fetchone()
        cursor.close()

        if existing_otp:
            otp = ''.join(random.choices(string.digits, k=6))
            cursor = connection.cursor()
            cursor.execute("UPDATE otps SET otp = %s WHERE email = %s", (otp, email))
            connection.commit()
            cursor.close()
        else:
            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=6))

            cursor = connection.cursor()
            cursor.execute("INSERT INTO otps (email, otp) VALUES (%s, %s)", (email, otp))
            connection.commit()
            cursor.close()

        # Construct the email content
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = "Password Reset OTP"
        body = f"Your OTP for password reset is: {otp}"
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, email, text)
        server.quit()
        return JSONResponse(content={'message': "OTP sent successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

# //////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////

@app.post("/verifyotp")
async def verify_otp(email: str = Form(...), otp: str = Form(...)):

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT otp FROM otps WHERE email = %s ORDER BY created_at DESC LIMIT 1", (email,))
        stored_otp = cursor.fetchone()
        cursor.close()
        
        if not stored_otp:
            return JSONResponse(content={'error': "OTP not found"}, status_code=404)


        
        stored_otp = stored_otp[0] 
        
        if otp != stored_otp:
            return JSONResponse(content={'error': "OTP not matched"}, status_code=400)

        
        return JSONResponse(content={'message': "OTP verified successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return HTTPException(status_code=500, content=str(e))
# //////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////

@app.post("/resetpassword")
async def reset_password(email: str = Form(...), otp: str = Form(...), new_password: str = Form(...)):
    try:
        # Verify OTP
        cursor = connection.cursor()
        cursor.execute("SELECT otp FROM otps WHERE email = %s ORDER BY created_at DESC LIMIT 1", (email,))
        stored_otp = cursor.fetchone()
        cursor.close()
        
        if not stored_otp:
            return JSONResponse(content={'error': "OTP not found"}, status_code=500)

        
        stored_otp = stored_otp[0]  # Extracting the OTP value from the tuple
        
        if otp != stored_otp:
            return JSONResponse(content={'error': "OTP does not match"}, status_code=400)

        
        
        # Update password
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        connection.commit()
        cursor.close()
        return JSONResponse(content={'message': "Password reset successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

# //////////////////////////////////////////////////////////////////////////////////////////////////

@app.post("/connect")
async def connect(user_id : str = Form(...)):

    try:
        connect_to_mqtt(user_id, "192.168.1.91", 1883)
        return JSONResponse(content={'message': "Connected"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
@app.post("/disconnect")
async def disconnect(user_id : str = Form(...)):
    try:
        if mqtt_clients[user_id]:
            mqtt_clients[user_id].disconnect()
            mqtt_clients[user_id].loop_stop()
            return JSONResponse(content={'message': "Disconnected"}, status_code=200)
        else:
            return JSONResponse(content={'error': "Not connected to MQTT"}, status_code=500)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

def send_message(user_id, topic, message):
    print(topic)
    try:
        if str(user_id) not in mqtt_clients:
            return KeyError(f"User ID {user_id} not found in MQTT clients")
        else:
            mqtt_clients[str(user_id)].publish(topic, message)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/switch")
async def switch(user_id : int = Form(...), switchNum : int = Form(...), switchId : int = Form(...), message : str=Form(...)):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT switches.id, switches.state, boards.boardname, boards.id FROM switches INNER JOIN boards ON switches.boardid = boards.id WHERE switches.id = %s AND switches.switchId = %s", (switchNum, switchId))
        switch = cursor.fetchone()
        print('test 1  ',switch[1])
        new_state = not switch[1]
        
        cursor.execute("UPDATE switches SET state = %s WHERE id = %s", (new_state, switchNum))
        connection.commit()
        cursor.close()
        print('test 2  ',switch[1])
        prefix = switch[2]+'/switch'
        send_message(user_id, f'{prefix}{str(switchId)}',message)
        return JSONResponse(content={'message': "Topic Executed"}, status_code=200)
   
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        print(f"Received message: {message.topic} {payload}")
        if message.topic == "prism/board1/touch1":
            print(str(message.payload))
    except Exception as e:
        traceback.print_exc()
    
@app.post("/touch")
async def touch(switchId: int = Form(...), id: int = Form(...)):
    cursor = connection.cursor()
    cursor.execute("SELECT switches.id, switches.state, boards.boardname, boards.id FROM switches INNER JOIN boards ON switches.boardid = boards.id WHERE switches.id = %s AND switches.switchId = %s", (id, switchId))
    switch = cursor.fetchone()
    new_state = switch[1]

    if new_state == 1:
        print('not here')
        cursor.execute("UPDATE switches SET state = %s WHERE id = %s", (0, id))
        connection.commit()
    else:
        print('here')
        cursor.execute("UPDATE switches SET state = %s WHERE id = %s", (1, id))
        connection.commit()
    cursor.close()


@app.get("/getBoards")
async def get_boards():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM boards")
    boards = cursor.fetchall()
    cursor.close()

    boards_list = [{"id": board[0], "boardname": board[1], "size": board[2], "available": board[3]} for board in boards]

    return JSONResponse(content={'boards': boards_list}, status_code=200)

@app.post("/roomused")
async def register_roomused(roomname: str = Form(...), boardid: int = Form(...)):
    print("Received form data:")
    print("Room Name:", roomname)
    print("Board ID:", boardid)

    cursor = connection.cursor()
    cursor.execute("INSERT INTO roomused (roomname, boardid) VALUES (%s, %s)", (roomname, boardid))
    connection.commit()
    cursor.close()

    return JSONResponse(content={'message': "Successfully Registered Room and Board"}, status_code=200)

@app.get("/getRooms")
async def get_rooms():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT rooms.id, rooms.roomname, boards.noOfAvailableSwitches,  boards.noOfSwitches, boards.id FROM rooms INNER JOIN boards ON rooms.boardid = boards.id")
        rooms = cursor.fetchall()
        cursor.close()
        print(rooms[0][3]-rooms[0][2])

        rooms_list = [{"id": room[0],"roomname": room[1], "switches": (room[3]-room[2]), "boardid": room[4]} for room in rooms]
        if not rooms:
            return JSONResponse(content={'error': "No rooms added"}, status_code=500)
        return JSONResponse(content={'rooms': rooms_list}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)


@app.post("/getSwitches")
async def get_switches(boardId: int = Form(...)):
    cursor = connection.cursor()
    cursor.execute("SELECT id, switchId, name, state FROM switches WHERE boardid = %s", (boardId,))
    switches = cursor.fetchall()

    cursor.execute("SELECT temp, moist, lumn FROM rooms WHERE boardid = %s", (boardId,))
    sensor_data = cursor.fetchone()

    cursor.close()

    if not switches:
        return JSONResponse(content={'error': "No switches added"}, status_code=500)

    switches_list = [{"id": switch[0], "switchId": switch[1], "name": switch[2], "state": switch[3]} for switch in switches]
    sensor_dict = {"temp": sensor_data[0], "moist": sensor_data[1], "lumn": sensor_data[2]} if sensor_data else {}
    response_content = {'switches': switches_list, 'sensor_data': sensor_dict}
    print("Data", response_content)

    return JSONResponse(content=response_content, status_code=200)

@app.get("/getAvailableBoards")
async def get_available_boards():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT boards.id, boards.boardname FROM boards LEFT JOIN rooms ON boards.id = rooms.boardid WHERE rooms.boardid IS NULL")
        available_boards = cursor.fetchall()
        cursor.close()

        available_boards_list = [{"id": board[0], "boardname": board[1]} for board in available_boards]

        return JSONResponse(content={'boards': available_boards_list}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/insertRoom")
async def insert_room(roomname: str = Form(...), boardid: int = Form(...)):
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO rooms (roomname, boardid) VALUES (%s, %s)", (roomname, boardid))
        connection.commit()
        cursor.close()
        
        return JSONResponse(content={'message': "Room inserted successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': "Error while adding room"}, status_code=500)

# @app.post("/getAvailableSwitches")
# async def get_switches(boardId: int = Form(...)):
#     cursor = connection.cursor()
#     cursor.execute("SELECT id, noOfAvailableSwitches FROM boards WHERE id = %s", (boardId,))
#     switch = cursor.fetchone()
#     cursor.close()

#     switches_list = [{"id": switch[0],"noOfSwitches": switch[1]}]

#     return JSONResponse(content={'switches': switches_list}, status_code=200)

@app.post("/getAvailableSwitches")
async def get_switches(boardId: int = Form(...)):
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT id FROM switches
            WHERE boardid = %s
            ORDER BY switchId
        """, (boardId,))
        switches_on_board = {switch for switch in cursor.fetchall()}
        print(switches_on_board)
        cursor.execute("""
            SELECT id FROM switches
            WHERE boardid IS NULL
            ORDER BY switchId
        """)
        all_switch_ids = {switch['id'] for switch in cursor.fetchall()}
        print(switches_on_board)
        available_switches = all_switch_ids - switches_on_board
        print(available_switches)
        available_switches = list(available_switches)[:4]
        print(available_switches)
        if not available_switches:
            return JSONResponse(content={'error': "No Switches Available for this board"}, status_code=404)
        
        return JSONResponse(content={'switches': available_switches}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/getSwitchesCount")
async def get_switches_count(boardId: int = Form(...)):
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM switches
            WHERE boardid = %s
        """, (boardId,))
        count_result = cursor.fetchone()
        print(count_result[0])
        
        if count_result[0] == 0:
            ids_list = [1, 2, 3, 4]
        else:
            cursor.execute("""
                SELECT DISTINCT switchId FROM switches
                WHERE boardid = %s
            """, (boardId,))
            added_switch_ids = [row[0] for row in cursor.fetchall()]
            
            all_switch_ids = [1, 2, 3, 4]
            other_ids = [id for id in all_switch_ids if id not in added_switch_ids]
            
            ids_list = other_ids
        print('\n\n Switch',ids_list)

        return JSONResponse(content={'ids_list': ids_list}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
# @app.post("/getAvailableSwitches")
# async def get_switches(boardId: int = Form(...)):
#         try:
#             cursor = connection.cursor()
#             cursor.execute("""
#                 SELECT boards.id, boards.noOfSwitches, boards.noOfAvailableSwitches, switches.switchId
#                 FROM boards
#                 JOIN switches ON boards.id = switches.boardId
#                 WHERE boards.id = %s
#             """, (boardId,))
#             switch = cursor.fetchone()
#             cursor.close()  # Close the cursor after fetching the results

#             print('\n\n Switch', switch)
#             # Further processing or returning the result
#         except Exception as e:
#             traceback_str = traceback.format_exc()
#             print("Error: ", traceback_str)
#             return JSONResponse(content={'error': str(e)}, status_code=500)



@app.post("/insertSwitch")
async def insert_switch(switchId: int = Form(...), name: str = Form(...), boardId: int = Form(...)):
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO switches (switchId, state, boardid, name) VALUES (%s, %s, %s, %s)", (switchId, 0, boardId, name))
        cursor.execute("UPDATE boards SET noOfAvailableSwitches = noOfAvailableSwitches - 1 WHERE id = %s", (boardId,))
        connection.commit()
        cursor.close()
        
        return JSONResponse(content={'message': "Switch inserted successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': "Getting error while adding switch"}, status_code=500)


@app.post("/removeSwitch")
async def remove_switch(switchId: int = Form(...), boardId: int = Form(...)):
    print(switchId)
    print(boardId)
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM switches WHERE switchId = %s AND boardid = %s", (switchId, boardId))
        connection.commit()
        cursor.execute("UPDATE boards SET noOfAvailableSwitches = noOfAvailableSwitches + 1 WHERE id = %s", (boardId,))
        connection.commit()
        cursor.close()
        return JSONResponse(content={'message': "Switch removed successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': "Getting error while removing switch"}, status_code=500)

@app.get("/fetchAllSwitchesStatistics")
async def fetch_all_switches_statistics():
    # try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, boardid, roomname FROM rooms")
        rooms = cursor.fetchall()

        # Iterate through each room and fetch switches associated with it
        switches_statistics = []
        for room in rooms:
            room_id, board_id, room_name = room
            # Fetch switches for the current room from switches table
            cursor.execute("SELECT name, state FROM switches WHERE boardid = %s", (board_id,))
            switches = cursor.fetchall()
            switches_statistics.append({
                'room_id': room_id,
                'boardid':  board_id,
                'room_name': room_name,
                'switches': switches,
            })
        print('\n\n',switches_statistics)
        cursor.close()

        return JSONResponse(content={'switches_statistics': switches_statistics}, status_code=200)
    # except Exception as e:
    #     traceback_str = traceback.format_exc()
    #     print("Error: ", traceback_str)
    #     return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/deleteRoom")
async def delete_room(roomId: int = Form(...), boardId: int = Form(...)):
    print(roomId)
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM switches WHERE boardid = (SELECT boardid FROM rooms WHERE id = %s)", (roomId,))
        connection.commit()
        cursor.execute("DELETE FROM rooms WHERE id = %s", (roomId,))
        connection.commit()
        cursor.execute("UPDATE boards SET noOfAvailableSwitches = 4 WHERE id = %s", (boardId,))
        connection.commit()
        cursor.close()

        return JSONResponse(content={'message': "Room and associated switches deleted successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': "Getting error while deleting room"}, status_code=500)

@app.post("/fetchGraph")
async def fetch_graph(frequency: int = Form(...)):
    try:
        data = []
        if frequency == 1:
            print(f'\n\n{frequency}\n\n')
            data = generate_data_for_hours()
        elif frequency == 2:
            print(f'\n\n{frequency}\n\n')
            data = generate_data_for_days_from_database(7)
        elif frequency == 3:
            data = generate_data_for_month_from_database(30)
        elif frequency == 4:
            data = generate_data_for_year_from_database(12)
        else:
            raise HTTPException(status_code=400, detail="Invalid frequency value")

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/testing")
async def testing(switchName: str = Form(...)):
    try:
        switchName1 = switchName
        switchName = '/'.join(switchName.split('/')[:-1])
        print(switchName)
        switch_name = switchName1[-1]
        print(switchName, switch_name)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM boards WHERE boardname = %s", (switchName,))
        result = cursor.fetchone()

        cursor.execute("SELECT * FROM switches WHERE boardid = %s AND switchId = %s", (result[0], switch_name,))
        switch_data = cursor.fetchone()

        print(switch_data)

        if switch_data[2] == 0:
            cursor.execute("UPDATE switches SET state = %s WHERE switchId = %s AND boardid = %s", (1, switch_data[1], result[0]))
            connection.commit()
        else:
            cursor.execute("UPDATE switches SET state = %s WHERE switchId = %s AND boardid = %s", (0, switch_data[1], result[0]))
            connection.commit()

        switchName=None
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

def generate_data_for_hours():

    try:
        labels = []
        values = []

        current_timestamp = datetime.now()
        cursor = connection.cursor()

        for i in range(24):
            start_timestamp = current_timestamp - timedelta(hours=i)
            end_timestamp = start_timestamp + timedelta(hours=1)
            query = "SELECT `usage` FROM realtime_usages WHERE timestamp >= %s AND timestamp < %s"
            cursor.execute(query, (start_timestamp, end_timestamp))
            minute_wise_data = cursor.fetchall()

            total_usage = sum(data[0] for data in minute_wise_data)
            total_count = len(minute_wise_data)

            average_usage = total_usage / total_count if total_count > 0 else 0

            labels.append(start_timestamp.strftime('%H:00'))
            values.append(average_usage)

        labels.reverse()
        values.reverse()
        
        cursor.close()


        data = {'labels': labels, 'values': values}
        return JSONResponse(content=data)

    except Exception as e:
        # Handle any errors
        print(f"An error occurred: {e}")
        raise e

def generate_data_for_days_from_database(number_of_days: int):

    try:
        labels = []
        values = []

        current_timestamp = datetime.now()

        cursor = connection.cursor()

        for i in range(number_of_days):
            start_date = current_timestamp - timedelta(days=i)
            end_date = start_date + timedelta(days=1)

            query = "SELECT consumption FROM consumptions WHERE date >= %s AND date < %s"
            cursor.execute(query, (start_date.date(), end_date.date()))
            daily_consumptions = cursor.fetchall()

            total_consumption = sum(data[0] for data in daily_consumptions)
            average_consumption = total_consumption / len(daily_consumptions) if daily_consumptions else 0

            day_name = start_date.strftime('%a')
            labels.append(day_name)
            values.append(average_consumption)

        labels.reverse()
        values.reverse()

        cursor.close()

        # print("Labels:", labels)
        # print("Values:", values)

        data = {'labels': labels, 'values': values}
        print("Data:", data)

        return JSONResponse(content=data)

    except Exception as e:
        # Handle any errors
        print(f"An error occurred: {e}")
        raise e

def generate_data_for_month_from_database(number_of_days: int):
    labels = []
    values = []

    try:
        start_date = datetime.now() - timedelta(days=number_of_days - 1)
        end_date = datetime.now()

        cursor = connection.cursor()

        query = "SELECT date, consumption FROM consumptions WHERE date >= %s AND date <= %s ORDER BY date"
        cursor.execute(query, (start_date.date(), end_date.date()))
        consumption_data = cursor.fetchall()

        current_date = start_date
        while current_date <= end_date:
            date_label = current_date.strftime('%m-%d')  # Format to show only month and day
            labels.append(date_label)

            consumption = 0  # Default value if no consumption data found
            for data in consumption_data:
                db_date = data[0].strftime('%m-%d')
                if db_date == date_label:
                    consumption = data[1]
                    values.append(consumption)
                    break

            current_date += timedelta(days=1)

        cursor.close()
        print("Labels:", labels)
        print("Values:", values)
        data = {'labels': labels, 'values': values}
        return JSONResponse(content=data)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

def generate_data_for_year_from_database(number_of_months: int) -> Dict[str, List]:
    labels = []
    values = []

    try:
        # Calculate start and end dates for the year
        end_date = datetime.now().replace(day=1, month=1, hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=number_of_months * 30)

        # Assuming you have a database connection
        cursor = connection.cursor()

        # Execute query to retrieve consumption data for the year
        query = "SELECT date, consumption FROM consumptions WHERE date >= %s AND date <= %s ORDER BY date"
        cursor.execute(query, (start_date.date(), end_date.date()))
        consumption_data = cursor.fetchall()

        # Group consumption data by month and year
        grouped_consumptions = {}
        for date, consumption in consumption_data:
            month_year = date.strftime('%b %y')
            grouped_consumptions[month_year] = grouped_consumptions.get(month_year, 0) + consumption

        # Iterate over each month in the year
        current_date = start_date
        while current_date <= end_date:
            month_year = current_date.strftime('%b %y')
            labels.append(month_year)
            values.append(grouped_consumptions.get(month_year, 0))

            current_date += timedelta(days=30) 

        cursor.close()
        print("Labels:", labels)
        print("Values:", values)
        data = {'labels': labels, 'values': values}
        return JSONResponse(content=data)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    