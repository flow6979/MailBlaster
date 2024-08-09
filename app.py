import logging
from flask import Flask

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)