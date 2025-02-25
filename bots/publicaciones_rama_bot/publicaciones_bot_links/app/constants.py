import os
from dotenv import load_dotenv

load_dotenv()

#URLS
WEBSITE_URL = os.getenv("WEBSITE_URL")

#RABBIT
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
SUB_QUEUE_NAME = os.getenv("SUB_QUEUE_NAME")
PUB_QUEUE_NAME = os.getenv("PUB_QUEUE_NAME")
PREFETCH_COUNT = int(os.getenv("PREFETCH_COUNT"))



