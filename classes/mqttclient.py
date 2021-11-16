import paho.mqtt.client as mqtt
from time import time

class MQTTClient:
    def __init__(self, user, password, host, port):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.client = mqtt.Client()

        self.mqtt_connect()

    def mqtt_connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        self.client.username_pw_set(self.user, password= self.password)

        self.client.connect(self.host, self.port, keepalive=600)

    def ts_string(self):
        return '{:.6f}'.format(time())
    
    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print('{} Connected to {} as {}'.format(
                self.ts_string(),
                self.settings["mqtt_host"],
                self.settings["mqtt_user"]))            
        else:
            print("Bad connection Returned code=",rc)
            print('{} Connect FAILED to {} as {} rc={}'.format(
                self.ts_string(),
                self.settings["mqtt_host"],
                self.settings["mqtt_user"]),
                rc)

    def on_disconnect(self,client, userdata, rc):
        print("\n{} acp_ttn_monitor disconnected".format(
            self.ts_string()))

    def on_publish(self, client, userdata, mid):
        print("\n{} Message published {}".format(
            self.ts_string(), mid))