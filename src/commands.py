import logging
from constants import START_MARKUP, WELCOME_MESSAGE

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("commands")

def command_handlers(bot):

    @bot.message_handler(commands=['start', 'hello'])
    def send_start(message):
        chat_id = message.chat.id
        message_id = message.message_id
        
        # Remove the markup from the previous message if it exists
        try:
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id - 1, reply_markup=None)
        except Exception as e: # Else do nothing
            logger.error(f"Error removing previous markup: {e}")

        bot.send_message(chat_id, "Welcome! What can I help you with?", reply_markup=START_MARKUP)

        