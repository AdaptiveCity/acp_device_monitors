#!/usr/bin/env python3

from monitors.ttngateway import *
import json

with open('secrets/settings.json', 'r') as settings_file:
    settings_data = settings_file.read()

    # parse file
settings = json.loads(settings_data)

ttnmonitor = TTNGateway(settings)