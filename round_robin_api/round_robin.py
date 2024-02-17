from flask import jsonify, request
import requests
import threading
import json
from round_robin_api.app import app
from common.utils import get_application_instances, Status

lock = threading.Lock()
application_instances = get_application_instances()
instance_index = 0

# instance_status = {instance: True for instance in application_instances}
# initialize instance_status with the status of each instance
# instance_status = {instance: Status.HEALTHY for instance in application_instances}
# print(instance_status)

def get_next_instance():
    global instance_index
    with lock:
        instance_length = len(application_instances)
        for _ in range(instance_length):
            instance_url = application_instances[instance_index]
            instance_index = (instance_index + 1) % instance_length
            if instance_status[instance_url]:
                app.logger.info(f"Using instance: {instance_url}")
                return instance_url
    return None


def make_request(instance_url, data):
    try:
        response = requests.post(instance_url + '/api', json=data, timeout=5)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error making request to {instance_url}: {e}")
        with lock:
            instance_status[instance_url] = False
        return None, 500


@app.route('/round-robin-api', methods=['POST'])
def round_robin_api():
    data = request.json
    instance_url = get_next_instance()
    
    if instance_url is None:
        return jsonify({"error": "All instances are down"}), 500
    
    response_data, status_code = make_request(instance_url, data)

    if status_code == 500:
        instance_url = get_next_instance()
        response_data, status_code = make_request(instance_url, data)

    return jsonify(response_data), status_code

