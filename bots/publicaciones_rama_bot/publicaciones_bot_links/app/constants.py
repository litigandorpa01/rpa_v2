import os
from dotenv import load_dotenv

load_dotenv()


#URLS
WEBSITE_URL = os.getenv("WEBSITE_URL")

#RABBIT
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")
PREFETCH_COUNT = int(os.getenv("PREFETCH_COUNT"))



