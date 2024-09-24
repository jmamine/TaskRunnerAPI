import logging

import docker
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

# Initialize Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Sets the level for the root logger

logger = logging.getLogger(__name__)
handler = logging.FileHandler('app.log')  # Log to a file
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



# Propagate the logging settings to all loggers
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

# Initialize BackgroundScheduler and Docker client


scheduler = BackgroundScheduler()
client = docker.from_env()