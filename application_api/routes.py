import os
import time
from flask import jsonify, request

from application_api.app import app
from common.utils import get_slow_ports, get_faulty_ports, APPLICATION_DELAY, HEALTH_CHECK_DELAY

# Application API endpoint
@app.route('/api', methods=['POST'])
def application_api():
    # Get the server port from the request
    server_port = request.environ.get('SERVER_PORT')
    slow_ports = get_slow_ports()

    # If the server port is in the slow ports list, delay the response (Simulate a slow response)
    if server_port in slow_ports:
        app.logger.info(f"Delaying response on port {server_port}")
        time.sleep(APPLICATION_DELAY)

    data = request.json
    return jsonify(data), 200

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    # Get the server port from the request
    server_port = request.environ.get('SERVER_PORT')
    slow_ports = get_slow_ports()
    status = "healthy"

    # If the server port is in the slow ports list, delay the response (Simulate a slow response)
    if server_port in slow_ports:
        app.logger.info(f"Delaying response on port {server_port}")
        status = "slow"
        time.sleep(HEALTH_CHECK_DELAY)
    
    return jsonify({"status": status}), 200