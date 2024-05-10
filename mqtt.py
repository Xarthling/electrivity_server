# Project: PRISM
# An Egde IoT System for home automation
# 
# Author: aitesam961
# 
# This is the main source code for RPI local client


import paho.mqtt.client as mqtt
import datetime
# MQTT Broker
mqttBroker = "10.42.0.1"
mqttPort = 1883
mqttClientID = "RPiClient1"

# MQTT Topics 

top_b1s1 = "prism/board1/switch1"  
top_b1s2 = "prism/board1/switch2"  
top_b1s3 = "prism/board1/switch3"  
top_b1s4 = "prism/board1/switch4" 

top_b2s1 = "prism/board2/switch1"
top_b2s2 = "prism/board2/switch2"
top_b2s3 = "prism/board2/switch3"
top_b2s4 = "prism/board2/switch4"

top_b3s1 = "prism/board3/switch1"  
top_b3s2 = "prism/board3/switch2"  
top_b3s3 = "prism/board3/switch3"  
top_b3s4 = "prism/board3/switch4" 

top_b4s1 = "prism/board4/switch1"
top_b4s2 = "prism/board4/switch2"
top_b4s3 = "prism/board4/switch3"
top_b4s4 = "prism/board4/switch4"


top_b1t1 = "prism/board1/touch1"  
top_b1t2 = "prism/board1/touch2"  
top_b1t3 = "prism/board1/touch3"  
top_b1t4 = "prism/board1/touch4" 

top_b2t1 = "prism/board2/touch1"  
top_b2t2 = "prism/board2/touch2"  
top_b2t3 = "prism/board2/touch3"  
top_b2t4 = "prism/board2/touch4" 

top_b3t1 = "prism/board3/touch1"  
top_b3t2 = "prism/board3/touch2"  
top_b3t3 = "prism/board3/touch3"  
top_b3t4 = "prism/board3/touch4" 

top_b4t1 = "prism/board4/touch1"  
top_b4t2 = "prism/board4/touch2"  
top_b4t3 = "prism/board4/touch3"  
top_b4t4 = "prism/board4/touch4" 

b1_pch_1 = "prism/board1/pwrch1"
b1_pch_2 = "prism/board1/pwrch2"
b1_pch_3 = "prism/board1/pwrch3"
b1_pch_4 = "prism/board1/pwrch4"

b2_pch_1 = "prism/board2/pwrch1"
b2_pch_2 = "prism/board2/pwrch2"
b2_pch_3 = "prism/board2/pwrch3"
b2_pch_4 = "prism/board2/pwrch4"

b3_pch_1 = "prism/board3/pwrch1"
b3_pch_2 = "prism/board3/pwrch2"
b3_pch_3 = "prism/board3/pwrch3"
b3_pch_4 = "prism/board3/pwrch4"

b4_pch_1 = "prism/board4/pwrch1"
b4_pch_2 = "prism/board4/pwrch2"
b4_pch_3 = "prism/board4/pwrch3"
b4_pch_4 = "prism/board4/pwrch4"


b1ttemp1= 0
b1ttemp2= 0
b1ttemp3= 0
b1ttemp4= 0

b2ttemp1= 0
b2ttemp2= 0
b2ttemp3= 0
b2ttemp4= 0

b3ttemp1= 0
b3ttemp2= 0
b3ttemp3= 0
b3ttemp4= 0

b4ttemp1= 0
b4ttemp2= 0
b4ttemp3= 0
b4ttemp4= 0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(top_b1t1)
    client.subscribe(top_b1t2)
    client.subscribe(top_b1t3)
    client.subscribe(top_b1t4)

    client.subscribe(top_b2t1)
    client.subscribe(top_b2t2)
    client.subscribe(top_b2t3)
    client.subscribe(top_b2t4)

    client.subscribe(top_b3t1)
    client.subscribe(top_b3t2)
    client.subscribe(top_b3t3)
    client.subscribe(top_b3t4)

    client.subscribe(top_b4t1)
    client.subscribe(top_b4t2)
    client.subscribe(top_b4t3)
    client.subscribe(top_b4t4)

    client.subscribe(b1_pch_1)
    client.subscribe(b1_pch_2)
    client.subscribe(b1_pch_3)
    client.subscribe(b1_pch_4)

    client.subscribe(b2_pch_1)
    client.subscribe(b2_pch_2)
    client.subscribe(b2_pch_3)
    client.subscribe(b2_pch_4)

    client.subscribe(b3_pch_1)
    client.subscribe(b3_pch_2)
    client.subscribe(b3_pch_3)
    client.subscribe(b3_pch_4)

    client.subscribe(b4_pch_1)
    client.subscribe(b4_pch_2)
    client.subscribe(b4_pch_3)
    client.subscribe(b4_pch_4)

    client.publish(top_b1s1, "off")
    client.publish(top_b1s2, "off")
    client.publish(top_b1s3, "off")
    client.publish(top_b1s4, "off")

    client.publish(top_b2s1, "off")
    client.publish(top_b2s2, "off")
    client.publish(top_b2s3, "off")
    client.publish(top_b2s4, "off")

    client.publish(top_b3s1, "off")
    client.publish(top_b3s2, "off")
    client.publish(top_b3s3, "off")
    client.publish(top_b3s4, "off")

    client.publish(top_b4s1, "off")
    client.publish(top_b4s2, "off")
    client.publish(top_b4s3, "off")
    client.publish(top_b4s4, "off")



def on_message(client, userdata, msg):
    now = datetime.datetime.now()
    print("Date and Time:", now.strftime("%Y-%m-%d %H:%M:%S"))
    # ------------------------------- B1
    global b1ttemp1
    global b1ttemp2
    global b1ttemp3
    global b1ttemp4
    if msg.topic == top_b1t1:
        if msg.payload == b'high':
            print("BEDROOM Touch-1 ACTIVE")
            if(b1ttemp1 ==0):
                client.publish(top_b1s1, 'on')
                print("BEDROOM LIGHT 1 Turned ON")
                b1ttemp1 =1
            else:
                client.publish(top_b1s1, 'off')
                print("BEDROOM LIGHT 1 Turned OFF")
                b1ttemp1 =0
    if msg.topic == top_b1t2:
        if msg.payload == b'high':
            print("BEDROOM Touch-2 ACTIVE")
            if(b1ttemp2 ==0):
                client.publish(top_b1s2, 'on')
                print("BEDROOM LIGHT 2 Turned ON")
                b1ttemp2 =1
            else:
                client.publish(top_b1s2, 'off')
                print("BEDROOM LIGHT 2 Turned OFF")
                b1ttemp2 =0
    if msg.topic == top_b1t3:
        if msg.payload == b'high':
            print("BEDROOM Touch-3 ACTIVE")
            if(b1ttemp3 ==0):
                client.publish(top_b1s3, 'on')
                print("BEDROOM LIGHT 3 Turned ON")
                b1ttemp3 =1
            else:
                client.publish(top_b1s3, 'off')
                print("BEDROOM LIGHT 3 Turned OFF")
                b1ttemp3 =0
    if msg.topic == top_b1t4:
        if msg.payload == b'high':
            print("BEDROOM Touch-4 ACTIVE")
            if(b1ttemp4 ==0):
                client.publish(top_b1s4, 'on')
                print("BEDROOM LIGHT 4 Turned ON")
                b1ttemp4 =1
            else:
                client.publish(top_b1s4, 'off')
                print("BEDROOM LIGHT 4 Turned OFF")
                b1ttemp4 =0

    
    # ------------------------------- B2

    global b2ttemp1
    global b2ttemp2
    global b2ttemp3
    global b2ttemp4
    if msg.topic == top_b2t1:
        if msg.payload == b'high':
            print("KITECHEN Touch-1 ACTIVE")
            if(b2ttemp1 ==0):
                client.publish(top_b2s1, 'on')
                print("KITECHEN LIGHT 1 Turned ON")
                b2ttemp1 =1
            else:
                client.publish(top_b2s1, 'off')
                print("KITECHEN LIGHT 1 Turned OFF")
                b2ttemp1 =0
    if msg.topic == top_b2t2:
        if msg.payload == b'high':
            print("KITECHEN Touch-2 ACTIVE")
            if(b2ttemp2 ==0):
                client.publish(top_b2s2, 'on')
                print("KITECHEN LIGHT 2 Turned ON")
                b2ttemp2 =1
            else:
                client.publish(top_b2s2, 'off')
                print("KITECHEN LIGHT 2 Turned OFF")
                b2ttemp2 =0
    if msg.topic == top_b2t3:
        if msg.payload == b'high':
            print("KITECHEN Touch-3 ACTIVE")
            if(b2ttemp3 ==0):
                client.publish(top_b2s3, 'on')
                print("KITECHEN LIGHT 3 Turned ON")
                b2ttemp3 =1
            else:
                client.publish(top_b2s3, 'off')
                print("KITECHEN LIGHT 3 Turned OFF")
                b2ttemp3 =0
    if msg.topic == top_b2t4:
        if msg.payload == b'high':
            print("KITECHEN Touch-4 ACTIVE")
            if(b2ttemp4 ==0):
                client.publish(top_b2s4, 'on')
                print("KITECHEN LIGHT 4 Turned ON")
                b2ttemp4 =1
            else:
                client.publish(top_b2s4, 'off')
                print("KITECHEN LIGHT 4 Turned OFF")
                b2ttemp4 =0

    # ------------------------------- B3

    global b3ttemp1
    global b3ttemp2
    global b3ttemp3
    global b3ttemp4
    if msg.topic == top_b3t1:
        if msg.payload == b'high':
            print("GARAGE Touch-1 ACTIVE")
            if(b3ttemp1 ==0):
                client.publish(top_b3s1, 'on')
                print("GARAGE LIGHT 1 Turned ON")
                b3ttemp1 =1
            else:
                client.publish(top_b3s1, 'off')
                print("GARAGE LIGHT  1 Turned OFF")
                b3ttemp1 =0
    if msg.topic == top_b3t2:
        if msg.payload == b'high':
            print("GARAGE Touch-2 ACTIVE")
            if(b3ttemp2 ==0):
                client.publish(top_b3s2, 'on')
                print("GARAGE LIGHT  2 Turned ON")
                b3ttemp2 =1
            else:
                client.publish(top_b3s2, 'off')
                print("GARAGE LIGHT  2 Turned OFF")
                b3ttemp2 =0
    if msg.topic == top_b3t3:
        if msg.payload == b'high':
            print("GARAGE Touch-3 ACTIVE")
            if(b3ttemp3 ==0):
                client.publish(top_b3s3, 'on')
                print("GARAGE LIGHT  3 Turned ON")
                b3ttemp3 =1
            else:
                client.publish(top_b3s3, 'off')
                print("GARAGE LIGHT  3 Turned OFF")
                b3ttemp3 =0
    if msg.topic == top_b3t4:
        if msg.payload == b'high':
            print("GARAGE Touch-4 ACTIVE")
            if(b3ttemp4 ==0):
                client.publish(top_b3s4, 'on')
                print("GARAGE LIGHT  4 Turned ON")
                b3ttemp4 =1
            else:
                client.publish(top_b3s4, 'off')
                print("GARAGE LIGHT  4 Turned OFF")
                b3ttemp4 =0
    
    # ------------------------------- B4

    global b4ttemp1
    global b4ttemp2
    global b4ttemp3
    global b4ttemp4
    if msg.topic == top_b4t1:
        if msg.payload == b'high':
            print("OUTDOORS Touch-1 ACTIVE")
            if(b4ttemp1 ==0):
                client.publish(top_b4s1, 'on')
                print("OUTDOORS LIGHT 1 Turned ON")
                b4ttemp1 =1
            else:
                client.publish(top_b4s1, 'off')
                print("OUTDOORS LIGHT  1 Turned OFF")
                b4ttemp1 =0
    if msg.topic == top_b4t2:
        if msg.payload == b'high':
            print("OUTDOORS Touch-2 ACTIVE")
            if(b4ttemp2 ==0):
                client.publish(top_b4s2, 'on')
                print("OUTDOORS LIGHT  2 Turned ON")
                b4ttemp2 =1
            else:
                client.publish(top_b4s2, 'off')
                print("OUTDOORS LIGHT  2 Turned OFF")
                b4ttemp2 =0
    if msg.topic == top_b4t3:
        if msg.payload == b'high':
            print("OUTDOORS Touch-3 ACTIVE")
            if(b4ttemp3 ==0):
                client.publish(top_b4s3, 'on')
                print("OUTDOORS LIGHT  3 Turned ON")
                b4ttemp3 =1
            else:
                client.publish(top_b4s3, 'off')
                print("OUTDOORS LIGHT  3 Turned OFF")
                b4ttemp3 =0
    if msg.topic == top_b4t4:
        if msg.payload == b'high':
            print("OUTDOORS Touch-4 ACTIVE")
            if(b4ttemp4 ==0):
                client.publish(top_b4s4, 'on')
                print("OUTDOORS LIGHT  4 Turned ON")
                b4ttemp4 =1
            else:
                client.publish(top_b4s4, 'off')
                print("OUTDOORS LIGHT  4 Turned OFF")
                b4ttemp4 =0

    # ------------------------------- Power Channel Readings

    if msg.topic == b1_pch_1:
        print("ROOM 1 Power CH1 : " , msg.payload.decode("utf-8"))
    if msg.topic == b1_pch_2:
        print("ROOM 1 Power CH2 : " , msg.payload.decode("utf-8"))
    if msg.topic == b1_pch_3:
        print("ROOM 1 Power CH3 : " , msg.payload.decode("utf-8"))
    if msg.topic == b1_pch_4:
        print("ROOM 1 Power CH4 : " , msg.payload.decode("utf-8"))

    if msg.topic == b2_pch_1:
        print("ROOM 2 Power CH1 : " , msg.payload.decode("utf-8"))
    if msg.topic == b2_pch_2:
        print("ROOM 2 Power CH2 : " , msg.payload.decode("utf-8"))
    if msg.topic == b2_pch_3:
        print("ROOM 2 Power CH3 : " , msg.payload.decode("utf-8"))
    if msg.topic == b2_pch_4:
        print("ROOM 2 Power CH4 : " , msg.payload.decode("utf-8"))


    if msg.topic == b3_pch_1:
        print("ROOM 3 Power CH1 : " , msg.payload.decode("utf-8"))
    if msg.topic == b3_pch_2:
        print("ROOM 3 Power CH2 : " , msg.payload.decode("utf-8"))
    if msg.topic == b3_pch_3:
        print("ROOM 3 Power CH3 : " , msg.payload.decode("utf-8"))
    if msg.topic == b3_pch_4:
        print("ROOM 3 Power CH4 : " , msg.payload.decode("utf-8"))

    if msg.topic == b4_pch_1:
        print("ROOM 4 Power CH1 : " , msg.payload.decode("utf-8"))
    if msg.topic == b4_pch_2:
        print("ROOM 4 Power CH2 : " , msg.payload.decode("utf-8"))
    if msg.topic == b4_pch_3:
        print("ROOM 4 Power CH3 : " , msg.payload.decode("utf-8"))
    if msg.topic == b4_pch_4:
        print("ROOM 4 Power CH4 : " , msg.payload.decode("utf-8"))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, mqttClientID)    # using V1 because V2 breaks the plugin
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqttBroker, mqttPort, 60)

client.loop_forever()