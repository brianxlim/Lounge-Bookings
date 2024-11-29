import logging
from constants import START_MARKUP, GET_MARKUP
from callbacks.get_availability import callback_get_availability
from callbacks.book import callback_book
from callbacks.unbook import callback_unbook

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("callbacks")

def callback_handlers(bot):

    callback_get_availability(bot)
    callback_book(bot)
    callback_unbook(bot)
