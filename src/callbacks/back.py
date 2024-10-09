import logging
from telebot import types

logger = logging.getLogger('callback (back)')

def callback_back(bot):

    def create_back_handler(text:str, markup: types.InlineKeyboardMarkup, state: str):
        @bot.callback_query_handler(func=lambda call: call.data == f'back_{state}'.lower().replace(' ', '_'))
        def back(call):

            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

            logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Going Back From {state}")

            bot.send_message(
                call.message.chat.id,
                text,
                reply_markup=markup
            )
    
    return create_back_handler