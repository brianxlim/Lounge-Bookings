import logging
from callbacks.back import callback_back
from constants import START_MARKUP, WELCOME_MESSAGE, CANCEL_MESSAGE, UTC_DIFF_HOURS
from config import get_chat_ids
from db import get_bookings_by_id, update_booking, get_bookings_by_date
from datetime import datetime, timedelta
from helpers import create_markup, create_buttons, validate_time_format
from callbacks.get_availability import get_availability_message

logger = logging.getLogger('callback (update)')
CHAT_ID, TOPIC_THREAD_ID = get_chat_ids(testing=True)

def callback_update(bot):
    callback_back(bot)(WELCOME_MESSAGE, START_MARKUP, "Update")

    @bot.callback_query_handler(func=lambda call: call.data == 'update_select')
    def update_select(call):

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Updating (Select Booking)")

        id = call.from_user.id
        bookings = get_bookings_by_id(id)

        if bookings.empty:
            bot.send_message(
                call.message.chat.id,
                "You have no bookings",
                reply_markup=START_MARKUP
            )
            return
        
        names = []
        callback_data = []
        bookings['level'] = bookings['level'].astype(int)

        # Data manipulation
        today = datetime.today() + timedelta(hours=UTC_DIFF_HOURS)
        bookings = bookings[bookings["timeslot_date"] >= today.date()]
        bookings = bookings.sort_values(by=['level', 'timeslot_date', 'timeslot_start_time'])

        for _, booking in bookings.iterrows():

            # Create name for button
            booking_start_str = booking["timeslot_start_time"].strftime("%H:%M")
            booking_end_str = booking["timeslot_end_time"].strftime("%H:%M")
            name = f"Level {booking["level"]} / {booking["timeslot_date"]} / {booking_start_str} - {booking_end_str}"

            # Create name for callback function
            callback = f"update_selected_{booking['level']}_{booking['booking_id']}_{booking['timeslot_date']}_{booking_start_str}_{booking_end_str}"
            names.append(name)
            callback_data.append(callback)

        bot.send_message(
            call.message.chat.id,
            "Select a booking to update",
            reply_markup=create_markup("UPDATE MARKUP", *create_buttons(names, callback_data))
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('update_selected'))
    def update(call):

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Updating")

        callback_info = call.data.split('_')
        level = callback_info[-5]
        booking_id = callback_info[-5]
        timeslot_date = datetime.strptime(callback_info[-3], "%Y-%m-%d")
        booking_start_time = callback_info[-2]
        booking_end_time = callback_info[-1]

        # Ask for the new start time
        bot.send_message(
            call.message.chat.id,
            f"Enter the new 24H start time (HHMM or HH:MM) for booking on:\n• Level {level}\n• {timeslot_date.strftime("%Y-%m-%d")}\n• {booking_start_time} - {booking_end_time} \n\n{CANCEL_MESSAGE}"
        )
        bot.register_next_step_handler(call.message, process_new_start_time, level, booking_id, timeslot_date)

    def process_new_start_time(message, level, booking_id, timeslot_date):
        new_start_time = message.text

        # Validate the new start time
        if not validate_time_format(new_start_time):
            bot.send_message(
                message.chat.id, 
                "Invalid time format. Please enter again (HHMM or HH:MM):"
            )
            
            bot.register_next_step_handler(
                message, 
                process_new_start_time, 
                level, 
                booking_id, 
                timeslot_date
            )
            return

        # Ask for the new end time
        bot.send_message(
            message.chat.id,
            "Enter the new 24H end time (HHMM or HH:MM):"
        )

        bot.register_next_step_handler(
            message, 
            process_new_end_time, 
            level, 
            booking_id, 
            new_start_time,
            timeslot_date
        )

    def process_new_end_time(message, level, booking_id, new_start_time, timeslot_date: datetime):
        new_end_time = message.text
        if new_end_time.lower().strip() == 'cancel':
            bot.send_message(
                message.chat.id,
                WELCOME_MESSAGE,
                reply_markup=START_MARKUP
            )
            return

        # Validate the new end time
        if not validate_time_format(new_end_time):
            bot.send_message(
                message.chat.id, 
                "Invalid time format. Please enter again (HHMM or HH:MM):"
            )

            bot.register_next_step_handler(
                message, 
                process_new_end_time, 
                level, 
                booking_id, 
                new_start_time
            )
            return
        
        # Convert timeslot_date, start_time, and end_time to datetime.time objects for comparison
        start_time_obj = datetime.strptime(new_start_time, '%H%M' if len(new_start_time) == 4 else '%H:%M').time()
        end_time_obj = datetime.strptime(new_end_time, '%H%M' if len(new_end_time) == 4 else '%H:%M').time()

        if end_time_obj <= start_time_obj:
            bot.send_message(
                message.chat.id, 
                f"End time must be after start time. Please enter again.\n\n {CANCEL_MESSAGE}"
            )

            bot.register_next_step_handler(
                message, 
                process_new_end_time, 
                level, 
                booking_id, 
                new_start_time
            )
            return

        # Check for time clashes using a helper function
        bookings = get_bookings_by_date(timeslot_date)
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
        if update_booking(level, booking_id, new_start_time, new_end_time):
            bot.send_message(
                message.chat.id, 
                f"Booking updated for level {level} on {timeslot_date.strftime("%Y-%m-%d")} to {new_start_time} - {new_end_time}.",
                reply_markup=START_MARKUP
            )

            # Update the group chat
            booking_date = timeslot_date.date()
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
