import logging
from callbacks.back import callback_back
from constants import START_MARKUP, BOOK_MARKUP_1, WELCOME_MESSAGE, CANCEL_MESSAGE, UTC_DIFF_HOURS, book_back_button
from helpers import validate_time_format, create_date_options, create_markup
from datetime import datetime, timedelta
from db import get_bookings_by_date, add_booking
from config import get_chat_ids
from callbacks.get_availability import get_availability_message
from zoneinfo import ZoneInfo

logger = logging.getLogger('callback (book)')
CHAT_ID, TOPIC_THREAD_ID = get_chat_ids(testing=True)

def callback_book(bot):

    callback_back(bot)(WELCOME_MESSAGE, START_MARKUP, "Book")

    @bot.callback_query_handler(func=lambda call: call.data == 'book_select_lounge')
    def select_lounge(call):
        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Booking Lounge (Select Lounge)")
        
        bot.send_message(
            call.message.chat.id,
            "Select lounge to book",
            reply_markup=BOOK_MARKUP_1
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('book_level'))
    def select_date(call):
        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Booking Lounge (Select Date)")

        level = call.data.split('_')[-1]
        date_options = create_date_options(callback_prefix=f"book_date_selected+{level}")
        date_options.append(book_back_button)

        bot.send_message(
            call.message.chat.id,
            "Select date to book",
            reply_markup=create_markup("BOOK LEVEL 2", *date_options)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('book_date_selected'))
    def handle_date_selection(call):
        # Extract selected_date and level from call.data
        # Expected format: 'book_date_selected+<selected_date>+<level>'
        data_parts = call.data.split('+')
        level = data_parts[1]
        selected_date = data_parts[2]

        # Now that we have both level and selected date, ask for the start time
        bot.send_message(
            call.message.chat.id,
            f"Enter the 24H start time for your booking (HHMM or HH:MM) for lounge level {level} on {selected_date}\n\n{CANCEL_MESSAGE}"
        )

        # Register the next step handler for the user's message
        bot.register_next_step_handler(
            call.message, 
            process_start_time, 
            level, 
            selected_date
        )

    # Handle start time
    def process_start_time(message, level, selected_date):
        start_time = message.text

        if start_time.lower().strip() == 'cancel':
            bot.send_message(
                message.chat.id,
                WELCOME_MESSAGE,
                reply_markup=START_MARKUP
            )
            return

        # Validate the start time format (HHMM or HH:MM)
        if not validate_time_format(start_time):
            bot.send_message(message.chat.id, F"Invalid time format. Please enter again (HHMM or HH:MM)\n\n{CANCEL_MESSAGE}")
            bot.register_next_step_handler(message, process_start_time, level, selected_date)
            return

        # Ask for the end time if start time is valid
        bot.send_message(
            message.chat.id, 
            f"Enter the 24H end time for your booking (HHMM or HH:MM)\n\n{CANCEL_MESSAGE}"
        )
        bot.register_next_step_handler(
            message, 
            process_end_time, 
            level, 
            selected_date, 
            start_time
        )
    
    def process_end_time(message, level, selected_date, start_time):
        end_time = message.text

        if end_time.lower().strip() == 'cancel':
            bot.send_message(
                message.chat.id,
                WELCOME_MESSAGE,
                reply_markup=START_MARKUP
            )
            return

        # Validate the end time format (HHMM or HH:MM)
        if not validate_time_format(end_time):
            bot.send_message(
                message.chat.id, 
                f"Invalid time format. Please enter again (HHMM or HH:MM)\n\n{CANCEL_MESSAGE}"
            )
            
            bot.register_next_step_handler(
                message, 
                process_end_time, 
                level, 
                selected_date, 
                start_time
            )
            return

        # Convert timeslot_date, start_time, and end_time to datetime.time objects for comparison
        start_time_obj = datetime.strptime(start_time, '%H%M' if len(start_time) == 4 else '%H:%M').time()
        end_time_obj = datetime.strptime(end_time, '%H%M' if len(end_time) == 4 else '%H:%M').time()

        if end_time_obj <= start_time_obj:
            bot.send_message(
                message.chat.id, 
                f"End time must be after start time. Please enter again.\n\n {CANCEL_MESSAGE}"
            )

            bot.register_next_step_handler(
                message, 
                process_end_time, 
                level, 
                selected_date, 
                start_time
            )
            return

        # Check for time clashes using a helper function
        bookings = get_bookings_by_date(selected_date)
        bookings = bookings[bookings['level'] == level]

        for _, booking in bookings.iterrows():
            booked_start = booking['timeslot_start_time']
            booked_end = booking['timeslot_end_time']
            if not (end_time_obj <= booked_start or start_time_obj >= booked_end):
                bot.send_message(
                    message.chat.id, 
                    f"Booking time clashes with existing booking from {booked_start.strftime("%H:%M")} to {booked_end.strftime("%H:%M")}. Try again with a different time."
                )
                return

        # If no clashes, insert booking
        user = message.from_user
        booking_date = datetime.now(ZoneInfo('UTC')) + timedelta(hours=UTC_DIFF_HOURS)
        if add_booking(level, booking_date, user.username, user.first_name, user.id, selected_date, start_time_obj, end_time_obj):
            bot.send_message(
                message.chat.id, 
                f"Booking confirmed for level {level} on {selected_date} from {start_time} to {end_time}."
            )

            # Update the group chat
            booking_date = datetime.strptime(selected_date, '%d/%m/%Y').date()
            today = datetime.today().date()
            if booking_date == today:
                response = get_availability_message(booking_date)
                bot.send_message(
                    CHAT_ID,
                    response,
                    message_thread_id=TOPIC_THREAD_ID
                )

        else:
            bot.send_message(
                message.chat.id, 
                "There was an error making the booking. Please try again."
            )
