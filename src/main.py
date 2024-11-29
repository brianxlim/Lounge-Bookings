import logging
import telebot
from config import BOT_TOKEN
from commands import command_handlers
from callbacks.callbacks import callback_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("main")
logger.info('Starting application...')

def main():
    bot = telebot.TeleBot(BOT_TOKEN)

    command_handlers(bot)
    
    callback_handlers(bot)

    bot.polling()

if __name__ == '__main__':
    main()
