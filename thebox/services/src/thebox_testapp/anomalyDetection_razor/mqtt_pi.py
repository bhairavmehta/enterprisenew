import paho.mqtt.client as mqtt
import time
import random
import datetime
 

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_publish(client, userdata, mid):
    print("published!")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.connect("jerrylia-lx-2.guest.corp.microsoft.com", 1834, 60)
data = [10.0,
10.6,
11.3,
11.9,
12.5,
13.1,
13.7,
14.3,
14.8,
15.4,
15.9,
16.4,
16.8,
17.3,
17.7,
18.1,
18.4,
18.8,
19.0,
19.3,
19.5,
19.7,
19.8,
19.9,
20.0,
20.0,
20.0,
19.9,
19.8,
19.7,
19.5,
19.3,
19.0,
18.8,
18.4,
18.1,
17.7,
17.3,
16.8,
16.4,
15.9,
15.4,
14.8,
14.3,
13.7,
13.1,
12.5,
11.9,
11.3,
10.6,
10.0,
9.4,
8.7,
8.1,
7.5,
6.9,
6.3,
5.7,
5.2,
4.6,
4.1,
3.6,
3.2,
2.7,
2.3,
1.9,
1.6,
1.2,
1.0,
0.7,
0.5,
0.3,
0.2,
0.1,
0.0,
0.0,
0.0,
0.1,
0.2,
0.3,
0.5,
0.7,
1.0,
1.2,
1.6,
1.9,
2.3,
2.7,
3.2,
3.6,
4.1,
4.6,
5.2,
5.7,
6.3,
6.9,
7.5,
8.1,
8.7,
9.4]
t = 0
while True:
    signal = data[t] + random.uniform(0,3)
    #{str(datetime.datetime.now())} + this
    message = str(time.strftime("%Y-%m-%d %H:%M:%S")) + "-" + str(signal)
    t = (t+1)%100
    print(message)
    client.publish("mhhd_s2",message)
    time.sleep(0.7)
