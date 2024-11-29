import logging
from telebot import types
from helpers import create_markup, create_date_options
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

logger = logging.getLogger("constants")
logger.info(f"TODAY (UTC TIMEZONE): {datetime.now(ZoneInfo('UTC'))}")

# Miscellaneous
KEEP_BOOKINGS_DAYS = 30
WELCOME_MESSAGE = "Welcome to Garuda Lounge Bot. How can I help you?"
EXIT_MESSAGE = "Thank you. Bye."
CANCEL_MESSAGE = "Enter 'cancel' to cancel booking'"

# DB
COLUMNS = [
    "booking_id",
    "booking_datetime",
    "level",
    "username",
    "first_name",
    "user_chat_id",
    "timeslot_date",
    "timeslot_start_time",
    "timeslot_end_time",
    "status"
]

# Timezone data
delta = datetime.now(ZoneInfo('UTC')) - datetime.now(ZoneInfo('Asia/Singapore'))
UTC_DIFF_HOURS = delta.total_seconds() / 3600
logger.info(f"TIME DIFFERENCE (HOURS): {round(UTC_DIFF_HOURS, 2)}")

# MARKUPS
get_availability_button = types.InlineKeyboardButton('Get Lounge Availability', callback_data='get_availability_select_date')
get_all_button = types.InlineKeyboardButton('Get All Dates', callback_data='get_availability_all_selected')
book_button = types.InlineKeyboardButton('Book Lounge', callback_data='book_select_lounge')
unbook_button = types.InlineKeyboardButton('Unbook Lounge', callback_data='unbook_select') # returns all the bookings he has
book_level_9_button = types.InlineKeyboardButton('\U0001F467\U0001F467 Level 9 \U0001F467\U0001F467', callback_data='book_level_9')
book_level_10_button = types.InlineKeyboardButton('\U0001F466\U0001F466 Level 10 \U0001F466\U0001F466', callback_data='book_level_10')
book_level_11_button = types.InlineKeyboardButton('\U0001F466\U0001F467 Level 11 \U0001F466\U0001F467', callback_data='book_level_11')
get_back_button = types.InlineKeyboardButton('Back', callback_data='back_get_availability')
book_back_button = types.InlineKeyboardButton('Back', callback_data='back_book')

START_MARKUP = create_markup('START MARKUP', get_availability_button, book_button, unbook_button)
BOOK_MARKUP_1 = create_markup('BOOK MARKUP LEVEL 1', book_level_9_button, book_level_10_button, book_level_11_button, book_back_button)
GET_MARKUP = create_markup('GET MARKUP', get_all_button, *create_date_options(callback_prefix="get_availability_date_selected"), get_back_button)
