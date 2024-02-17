import logging
from flask import Flask

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
handler = logging.FileHandler('application_api.log')
app.logger.addHandler(handler)    

# Importing routes after app creation to avoid circular imports
from application_api import routes
