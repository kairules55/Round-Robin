import threading
import time
import requests
from round_robin_api.round_robin import application_instances, instance_status, lock as shared_lock
from round_robin_api.app import app

HEALTH_CHECK_INTERVAL = 60  # Interval for health checks in seconds
HEALTH_CHECK_TIMEOUT = 5  # Timeout for health check requests in seconds
MAX_RETRY_ATTEMPTS = 3  # Maximum number of retry attempts for failed health checks

def health_check_instance(instance_url):
    retry_attempt = 0
    while retry_attempt < MAX_RETRY_ATTEMPTS:
        try:
            response = requests.get(instance_url + '/health', timeout=HEALTH_CHECK_TIMEOUT)
            app.logger.info(f"Health check for instance {instance_url}: {response.json()} : {response.status_code}")
            with shared_lock:
                if response.status_code == 200:
                    instance_status[instance_url] = True
                    return True
                else:
                    app.logger.info(f"Health check failed for instance {instance_url}: {response.status_code}")
                    instance_status[instance_url] = False
                    return False
        except requests.exceptions.RequestException as e:
            with shared_lock:
                instance_status[instance_url] = False
                app.logger.error(f"Error checking health of instance {instance_url}: {e}")
            time.sleep(1)
            retry_attempt += 1
    with shared_lock:
        app.logger.error(f"Health check failed for instance {instance_url} after {MAX_RETRY_ATTEMPTS} attempts.")
        instance_status[instance_url] = False
    return False

def health_check():
    while True:
        for instance_url in application_instances:
            health_check_instance(instance_url)
        time.sleep(HEALTH_CHECK_INTERVAL)

