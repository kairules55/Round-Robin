from flask import jsonify, request
import requests
import threading
import json
import time
from round_robin_api.app import app
from application_api.app import app as application_app
from common.utils import get_application_instances, get_application_url,  Status, HEALTH_CHECK_TIMEOUT, HEALTH_CHECK_INTERVAL, APPLICATION_TIMEOUT, MAX_RETRY

# Setup threads and application instances
lock = threading.Lock()
application_instances = get_application_instances()
instance_index = 0
instance_status = {
    instance: Status.HEALTHY for instance in application_instances}


def get_instances(status: Status):
    global instance_index
    with lock:
        instance_length = len(application_instances)
        for _ in range(instance_length):
            instance_url = application_instances[instance_index]
            instance_index = (instance_index + 1) % instance_length
            if instance_status[instance_url] == status:
                app.logger.info(f"Using instance: {instance_url}")
                return instance_url
    return None


def get_next_instance():
    instance_url = get_instances(Status.HEALTHY)
    if instance_url is None:
        instance_url = get_instances(Status.SLOW)
    return instance_url


def make_request(method, instance_url, endpoint, data=None, timeout=5):
    if method.lower() == 'get':
        return requests.get(instance_url + endpoint, timeout=timeout)
    elif method.lower() == 'post':
        return requests.post(instance_url + endpoint, json=data, timeout=timeout)
    else:
        raise ValueError("Invalid method. Expected 'get' or 'post'.")


def update_status(instance_url, status, status_code=None):
    with lock:
        instance_status[instance_url] = status
        app.logger.info(
            f"Instance {instance_url} status: {instance_status[instance_url]}")
    return None, status_code


def make_request_and_update_status(method, instance_url, endpoint, data=None, timeout=5):
    try:
        response = make_request(method, instance_url, endpoint, data, timeout)
        update_status(instance_url, Status.HEALTHY, response.status_code)
        return response.json(), response.status_code
    except requests.exceptions.Timeout as e:
        return update_status(instance_url, Status.SLOW, 408)
    except requests.exceptions.RequestException as e:
        return update_status(instance_url, Status.DOWN, 500)


def health_check_instance(instance_url):
    _, status_code = make_request_and_update_status(
        'get', instance_url, '/health', timeout=HEALTH_CHECK_TIMEOUT)


def health_check():
    while True:
        for instance_url in application_instances:
            health_check_instance(instance_url)
        time.sleep(HEALTH_CHECK_INTERVAL)


@app.route('/add-server', methods=['POST'])
def add_server():
    data = request.json
    port = data.get('port')
    if port:
        # Add the new server to the list of application instances
        new_server = f"{get_application_url()}:{port}"
        with lock:
            application_instances.append(new_server)
            instance_status[new_server] = Status.HEALTHY

        # Start the new server in a separate thread
        thread = threading.Thread(
            target=application_app.run, kwargs={"port": port})
        thread.start()
        app.logger.info(f"Server added on port {port}")
        return jsonify({"message": f"Server added on port {port}"}), 200
    else:
        app.logger.error("Port not provided")
        return jsonify({"error": "Port not provided"}), 400


@app.route('/round-robin-api', methods=['POST'])
def round_robin_api():
    data = request.get_json(force=True)
    retry_count = 0

    while retry_count < MAX_RETRY:
        instance_url = get_next_instance()
        if not instance_url:
            app.logger.error("All instances are down")
            return jsonify({"error": "All instances are down"}), 500

        response_data, status_code = make_request_and_update_status(
            'post', instance_url, '/api', data, APPLICATION_TIMEOUT)
        if status_code == 200:
            return jsonify(response_data), status_code

        retry_count += 1
        app.logger.warning(
            f"Request failed, retrying... ({retry_count}/{MAX_RETRY})")

    app.logger.error("All instances are down after max retries")
    return jsonify({"error": "All instances are down after max retries"}), 500
