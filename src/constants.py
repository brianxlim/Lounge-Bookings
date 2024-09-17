from telebot import types
from helpers import create_markup, create_date_options

# Miscellaneous
KEEP_BOOKINGS_DAYS = 30
WELCOME_MESSAGE = "Welcome to Garuda Lounge Bot. How can I help you?"
CANCEL_MESSAGE = "Enter 'cancel' to cancel booking'"

# MARKUPS
get_availability_button = types.InlineKeyboardButton('Get Lounge Availability', callback_data='get_availability_select_date')
book_button = types.InlineKeyboardButton('Book Lounge', callback_data='book_select_lounge')
unbook_button = types.InlineKeyboardButton('Unbook Lounge', callback_data='unbook_select') # returns all the bookings he has
update_button = types.InlineKeyboardButton('Update Booking', callback_data='update') # returns all the bookings he has
book_level_9_button = types.InlineKeyboardButton('\U0001F467\U0001F467 Level 9 \U0001F467\U0001F467', callback_data='book_level_9')
book_level_10_button = types.InlineKeyboardButton('\U0001F466\U0001F466 Level 10 \U0001F466\U0001F466', callback_data='book_level_10')
book_level_11_button = types.InlineKeyboardButton('\U0001F466\U0001F467 Level 11 \U0001F466\U0001F467', callback_data='book_level_11')
get_back_button = types.InlineKeyboardButton('Back', callback_data='back_get_availability')
book_back_button = types.InlineKeyboardButton('Back', callback_data='back_book')
update_button = types.InlineKeyboardButton('Update Booking', callback_data='update_select')

START_MARKUP = create_markup('START MARKUP', get_availability_button, book_button, unbook_button, update_button)
BOOK_MARKUP_1 = create_markup('BOOK MARKUP LEVEL 1', book_level_9_button, book_level_10_button, book_level_11_button, book_back_button)
GET_MARKUP = create_markup('GET MARKUP', *create_date_options(callback_prefix="get_availability_date_selected"), get_back_button)
