import logging
from flask import Flask

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
handler = logging.FileHandler('round_robin.log')
app.logger.addHandler(handler)    

from round_robin_api import round_robin 

