import json
import requests
import sys
from time import sleep, time
import paho.mqtt.client as mqtt

class ACPTTNMonitor:
    def __init__(self, settings):
        self.settings = settings
        self.headers = {'Authorization': settings['api_key'], "grant_type": "authorization_code"}
        self.client = mqtt.Client()

        self.connect_mqtt()

        self.start_gateway_monitor()
        # self.start_sensor_monitor()

    ###################################
    #         MQTT Block              #
    ###################################

    def connect_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        user = self.settings["mqtt_user"]
        password = self.settings["mqtt_password"]
        host = self.settings["mqtt_host"]
        port = self.settings["mqtt_port"]

        self.client.username_pw_set(user, password=password)

        self.client.connect(host, port, keepalive=30)

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

    
    # Monitor Gateways

    def start_gateway_monitor(self):

        while True:
            gateway_status = {'total':0, 'connected':0, 'disconnected':0, 'gateways': {}}

            all_gateway_response = requests.get(self.settings['gateway_url'].format(self.settings['user_id']), headers= self.headers)

            disconnected, connected = 0, 0

            for gateway in all_gateway_response.json()['gateways']:
                gateway_id = gateway['ids']['gateway_id']
                status_response = requests.get(self.settings['gateway_status_url'].format(gateway_id), headers= self.headers)
                
                if 'code' in list(status_response.json().keys()):
                    disconnected+=1
                    gateway_status['gateways'].update(
                            {
                                gateway_id: {
                                    'gateway_id': gateway_id, 
                                    'gateway_status': 'disconnected',
                                    'gateway_status_message': ''}
                            }
                        )
                else:
                    connected+=1
                    gateway_status['gateways'].update(
                            {
                                gateway_id: {
                                    'gateway_id': gateway_id, 
                                    'gateway_status': 'connected',
                                    'gateway_status_message': status_response.json()['last_uplink_received_at']}
                            }
                        )

            gateway_status['connected'] = connected
            gateway_status['disconnected'] = disconnected
            gateway_status['total'] = connected + disconnected

            monitor_message = {
                'acp_ts': str(time()),
                'acp_id': self.settings['gateway_acp_id'],
                'acp_type': self.settings['acp_type_id'],
                'payload_cooked': gateway_status
            }
            print(monitor_message['acp_id'])
            self.client.publish(self.settings['gateway_topic'], json.dumps(monitor_message), qos=0)
            sleep(10)