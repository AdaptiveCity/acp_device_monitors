import json
import requests
import sys
from time import sleep, time
from classes.mqttclient import MQTTClient
from classes.util import get_time_since_epoch

class TTNGateway:
    def __init__(self, settings):
        self.settings = settings
        self.headers = {'Authorization': settings['api_key'], "grant_type": "authorization_code"}
        self.client = MQTTClient(settings['mqtt_user'], settings['mqtt_password'], settings['mqtt_host'], settings['mqtt_port']).client
        self.gateways = self.initialize_gateway_status()

        self.start_gateway_monitor()

    
    def initialize_gateway_status(self):
        gateways = {}

        all_gateway_response = requests.get(self.settings['gateway_url'].format(self.settings['user_id']), headers= self.headers)

        for gateway in all_gateway_response.json()['gateways']:
                gateway_id = gateway['ids']['gateway_id']
                status_response = requests.get(self.settings['gateway_status_url'].format(gateway_id), headers= self.headers)

                if 'code' in list(status_response.json().keys()):
                    gateways.update(
                        {
                            gateway_id: {
                                'status': 'disconnected'
                            }
                        }
                    )
                else:
                    gateways.update(
                        {
                            gateway_id: {
                                'status': 'connected'
                            }
                        }
                    )
        return gateways

    # Monitor Gateways
    def start_gateway_monitor(self):
        timer = 0
        while True:
            event_flag = False
            gateway_status = {'total':0, 'connected':0, 'disconnected':0, 'gateways': {}}
            event = {'up':[], 'down':[]}

            all_gateway_response = requests.get(self.settings['gateway_url'].format(self.settings['user_id']), headers= self.headers)

            disconnected, connected = 0, 0

            for gateway in all_gateway_response.json()['gateways']:
                gateway_id = gateway['ids']['gateway_id']
                status_response = requests.get(self.settings['gateway_status_url'].format(gateway_id), headers= self.headers)
                
                if 'code' in list(status_response.json().keys()):
                    disconnected+=1

                    if self.gateways[gateway_id]['status'] == 'connected':
                        event['down'].append(gateway_id)
                        event_flag = True

                    gateway_status['gateways'].update(
                            {
                                gateway_id: {
                                    'gateway_id': gateway_id, 
                                    'gateway_status': 'disconnected',
                                    'gateway_status_message': ''}
                            }
                        )
                    self.gateways[gateway_id]['status'] = 'disconnected'
                else:
                    last_mesage_time = get_time_since_epoch(status_response.json()['last_uplink_received_at'])
                    if time() - last_mesage_time < 60:
                        if self.gateways[gateway_id]['status'] == 'disconnected':
                            event['up'].append(gateway_id)
                            event_flag = True
                        connected+=1
                        gateway_status['gateways'].update(
                                {
                                    gateway_id: {
                                        'gateway_id': gateway_id, 
                                        'gateway_status': 'connected',
                                        'gateway_status_message': last_mesage_time
                                    }
                                }
                            )
                        self.gateways[gateway_id] = {'status': 'connected'}
                    else:
                        if self.gateways[gateway_id]['status'] == 'connected':
                            event['down'].append(gateway_id)
                            event_flag = True
                        self.gateways[gateway_id]['status'] = 'disconnected'
                        disconnected+=1
                        gateway_status['gateways'].update(
                                {
                                    gateway_id: {
                                        'gateway_id': gateway_id, 
                                        'gateway_status': 'disconnected',
                                        'gateway_status_message': last_mesage_time
                                    }
                                }
                            )

            if event_flag:
                gateway_status['connected'] = connected
                gateway_status['disconnected'] = disconnected
                gateway_status['total'] = connected + disconnected
                acp_event = {
                    'up': {
                        'acp_event_type': 'up',
                        'acp_event_value': event['up']
                    },
                    'down': {
                        'acp_event_type': 'down',
                        'acp_event_value': event['down']
                    }
                }

                monitor_event_message = {
                    'acp_ts': str(time()),
                    'acp_id': self.settings['gateway_acp_id'],
                    'acp_type': self.settings['acp_type_id'],
                    'acp_event': acp_event,
                    'payload_cooked': gateway_status
                }
                print('Event Message:', monitor_event_message)
                self.client.publish(self.settings['gateway_topic'], json.dumps(monitor_event_message), qos=0)
            elif timer%120 == 0:
                gateway_status['connected'] = connected
                gateway_status['disconnected'] = disconnected
                gateway_status['total'] = connected + disconnected

                monitor_event_message = {
                    'acp_ts': str(time()),
                    'acp_id': self.settings['gateway_acp_id'],
                    'acp_type': self.settings['acp_type_id'],
                    'payload_cooked': gateway_status
                }
                print('Periodic Message:', monitor_event_message)
                self.client.publish(self.settings['gateway_topic'], json.dumps(monitor_event_message), qos=0)

            sleep(10)
            timer+=10
            print(timer)