import logging
from constants import START_MARKUP, WELCOME_MESSAGE

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("commands")

def command_handlers(bot):

    @bot.message_handler(commands=['start', 'hello'])
    def start(message):
        logger.info(f"{message.from_user.first_name} (@{message.from_user.username}) Started Bot")

        bot.send_message(
            message.chat.id, 
            text=WELCOME_MESSAGE, 
            reply_markup=START_MARKUP
        )
