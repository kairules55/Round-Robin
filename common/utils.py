import json
import requests
from enum import Enum

class Status(Enum):
    HEALTHY = 200
    SLOW = 408
    DOWN = 500

with open('config.json') as f:
    config = json.load(f)

HEALTH_CHECK_TIMEOUT = config['healthcheck_config']['timeout']
HEALTH_CHECK_INTERVAL = config['healthcheck_config']['interval']
APPLICATION_TIMEOUT = config['application_config']['timeout']
HEALTH_CHECK_DELAY = config['healthcheck_config']['simulated_delay']
APPLICATION_DELAY = config['application_config']['simulated_delay']

def get_application_instances():
    application_url = get_application_url()
    application_ports = get_application_ports()
    application_instances = [f"{application_url}:{port}" for port in application_ports]
    return application_instances

def get_application_ports():
    return config['application_config']['ports']

def get_application_url():
    return config['application_config']['url']

def get_round_robin_port():
    return config['round_robin_config']['port']

def get_slow_ports():
    return config['application_config']['slow_simulation']

def get_faulty_ports():
    return config['application_config']['down_simulation']


