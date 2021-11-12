from monitors.ttngateway import TTNGateway
import json

with open('secrets/settings.json', 'r') as settings_file:
    settings_data = settings_file.read()

    # parse file
settings = json.loads(settings_data)

monitor = TTNGateway(settings)