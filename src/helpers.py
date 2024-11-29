import logging
from telebot import types
from datetime import datetime, timedelta
import re
import calendar

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("helpers")

def validate_time_format(time_str, end=False):
    """
    Validates if the given time is in 'HHMM' or 'HH:MM' format.
    Returns True if valid, False otherwise.
    """
    # Regular expressions for HHMM and HH:MM formats
    hhmm_format = re.compile(r'^\d{4}$')
    hh_mm_format = re.compile(r'^\d{2}:\d{2}$')

    try:
        if hhmm_format.match(time_str):
            datetime.strptime(time_str, '%H%M')
            return True
        elif hh_mm_format.match(time_str):
            datetime.strptime(time_str, '%H:%M')
            return True
        else:
            return False
    except ValueError:
        return False

def create_markup(name, *buttons):
    try:
        markup = types.InlineKeyboardMarkup()

        for button in buttons:
            markup = markup.add(button)

        logger.info(f"Successfully created {name}")
        return markup
    
    except Exception as e:
        logger.error(f"Error while creating markup {name}: {e}")
        return e

def create_buttons(names: list[str], callback_data: list[str], purpose = 'unknown'):
    """
    Returns a list of buttons based on parameters
    """
    if len(names) != len(callback_data):
        logger.info("names and callback_data arguments have unequal lengths")

    logger.info(f'Creating buttons for {purpose}')

    buttons = []
    for i in range(len(names)):
        button = types.InlineKeyboardButton(names[i], callback_data=callback_data[i])
        buttons.append(button)

    return buttons

def create_date_options(days = 7, callback_prefix = "date_selected"):
    """
    Returns a list of buttons for markup options
    """
    buttons = []

    for i in range(days):
        day = datetime.today() + timedelta(days=i)
        day_str = day.strftime("%d/%m/%Y")
        option = types.InlineKeyboardButton(day_str + " (Today)" if i == 0 else day_str + f" ({calendar.day_name[day.weekday()][:3]})", callback_data=f"{callback_prefix}+{day_str}")
        buttons.append(option)
    
    return buttons

