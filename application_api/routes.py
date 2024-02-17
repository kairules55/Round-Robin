import os
from flask import jsonify, request

from application_api.app import app
from common.utils import get_slow_ports, get_faulty_ports

# Application API endpoint
@app.route('/api', methods=['POST'])
def application_api():
    server_port = request.environ.get('SERVER_PORT')
    app.logger.info(f"Received request on port {request.environ.get('SERVER_PORT')}")
    data = request.json
    return jsonify(data), 200

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    server_port = request.environ.get('SERVER_PORT')
    slow_ports = get_slow_ports()
    faulty_ports = get_faulty_ports()
    app.logger.info(f"slow ports {slow_ports} {type(slow_ports)} {type(slow_ports[0])}")
    app.logger.info(f"Health check on port {server_port} {type(server_port)}")
    if server_port in slow_ports:
        return jsonify({"status": "slow"}), 300
    elif server_port in faulty_ports:
        return jsonify({"status": "down"}), 500
    else:
        return jsonify({"status": "healthy"}), 200