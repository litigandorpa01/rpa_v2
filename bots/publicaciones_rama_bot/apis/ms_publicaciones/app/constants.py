import os
from dotenv import load_dotenv

load_dotenv()

#RABBIT
RABBITMQ_HOST  = os.getenv("RABBITMQ_HOST")
PUB_QUEUE_NAME = os.getenv("PUB_QUEUE_NAME")

#DB
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_SERVICE_NAME = os.getenv("DB_SERVICE_NAME")

