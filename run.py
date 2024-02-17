
from round_robin_api.app import app as round_robin_app
from round_robin_api.health_check import health_check
from application_api.app import app as application_app
from common.utils import get_application_ports
import threading

if __name__ == '__main__':
    # Start the Round Robin API in a separate thread
    round_robin_thread = threading.Thread(target=round_robin_app.run, kwargs={"port": 5000})
    round_robin_thread.start()

    # Start the health check in a separate thread
    health_check_thread = threading.Thread(target=health_check)
    health_check_thread.daemon = True
    health_check_thread.start()
    
    # Start each Application API in a separate thread
    application_ports = get_application_ports()
    application_threads = []
    for port in application_ports:
        thread = threading.Thread(target=application_app.run, kwargs={"port": port})
        application_threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    round_robin_thread.join()
    health_check_thread.join()
    for thread in application_threads:
        thread.join()

