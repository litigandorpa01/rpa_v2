import os
from dotenv import load_dotenv

load_dotenv()

#KEYS
CAPMONSTER_KEY = os.getenv("CAPMONSTER_KEY")

#URLS
WEBSITE_URL = os.getenv("WEBSITE_URL")
WEBSITE_KEY = os.getenv("WEBSITE_KEY")
PAGE_ACTION= os.getenv("PAGE_ACTION")

#RABBIT
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")
PREFETCH_COUNT = int(os.getenv("PREFETCH_COUNT"))

#SCRAPPERS
CONSULT_ATTEMPS= int(os.getenv("CONSULT_ATTEMPS"))



