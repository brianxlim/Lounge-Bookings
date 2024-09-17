import logging
import os
from dotenv import load_dotenv

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("config")
logger.info('Retrieving environment variables')

try:
    load_dotenv()

    BOT_TOKEN = os.getenv('BOT_TOKEN')
    TEST_CHAT_ID = os.getenv('TEST_CHAT_ID')
    TEST_TOPIC_THREAD_ID = os.getenv('TEST_TOPIC_THREAD_ID')
    PRODUCTION_CHAT_ID = os.getenv('PRODUCTION_CHAT_ID')
    PRODUCTION_TOPIC_THREAD_ID = os.getenv('PRODUCTION_TOPIC_THREAD_ID')
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    logger.info('Successfully retrieved environment variables')

except Exception as e:
    logger.info(f'Error while retrieving environment variables: {e}')

def get_chat_ids(testing = True):
    return (TEST_CHAT_ID, TEST_TOPIC_THREAD_ID) if testing else (PRODUCTION_CHAT_ID, PRODUCTION_TOPIC_THREAD_ID)
