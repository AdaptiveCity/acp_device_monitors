# Adaptive City Program Device Status Monitor

## Overview
This project creates virtual sensors that periodically or on occurrence of an event sends device status to the ACP platform. These virtual sensors show a similar chart as other sensors, highlighting the number of `connected` and `disconnected` devices of a certain category. The devices could be:
+ TTN gateways
+ TTN sensors belonging to a certain application
+ Other gateways
+ Other sensors
+ Servers

## Prerequisites
+ Setup the `acp_prod` database (https://github.com/AdaptiveCity/acp_data_strategy/blob/master/INSTALLATION.md).
+ Use the `acp_db_manager` repo to add the new sensor_type and sensor metadata (https://github.com/AdaptiveCity/acp_db_manager). The metadata information can be obtained from existing servers.
+ Get the `settings.json` file from an existing server.

## Installation
Note we are using the venv package so any python installs are local to this repo. You have to remember to enter the command source `venv/bin/activate` in your shell for the packages to be found.

As `acp_prod` user setup the repository:

```
git clone https://github.com/AdaptiveCity/acp_device_monitors.git
cd acp_device_monitors
python -m venv venv
source venv/bin/activate
python -m pip install pip --upgrade
python -m pip install wheel
python -m pip install -r requirements.txt
```

Run the monitors using:
```
./run.sh
```