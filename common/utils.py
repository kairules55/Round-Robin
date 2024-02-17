import json
from enum import Enum

class Status(Enum):
    SLOW = 200
    DOWN = 500
    HEALTHY = 200

with open('config.json') as f:
    config = json.load(f)

def get_application_instances():
    application_url = get_application_url()
    application_ports = get_application_ports()
    application_instances = [f"{application_url}:{port}" for port in application_ports]
    return application_instances

def get_application_ports():
    return config['application_config']['ports']

def get_application_url():
    return config['application_config']['url']

def get_slow_ports():
    return config['application_config']['slow']

def get_faulty_ports():
    return config['application_config']['down']

