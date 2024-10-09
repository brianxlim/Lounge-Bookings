import logging
from callbacks.back import callback_back
from constants import START_MARKUP, WELCOME_MESSAGE
from config import get_chat_ids
from db import get_bookings_by_id, cancel_booking
from helpers import create_buttons, create_markup
from datetime import datetime, timedelta
from callbacks.get_availability import get_availability_message
from zoneinfo import ZoneInfo

logger = logging.getLogger('callback (unbook)')
CHAT_ID, TOPIC_THREAD_ID = get_chat_ids(testing=True)

def callback_unbook(bot):

    callback_back(bot)(WELCOME_MESSAGE, START_MARKUP, "Unbook")

    @bot.callback_query_handler(func=lambda call: call.data == 'unbook_select')
    def unbook_select(call):
        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Unbooking (Select Booking)")

        id = call.from_user.id
        bookings = get_bookings_by_id(id)

        # Filter for valid bookings, i.e. not expired
        today_sgt = datetime.now(ZoneInfo("Asia/Singapore")).date() # Get current time in Singapore (SGT)
        bookings = bookings[bookings["timeslot_date"] >= today_sgt]


        if bookings.empty:
            logger.info("No bookings found to unbook")
            bot.send_message(
                call.message.chat.id,
                "You have no bookings",
                reply_markup=START_MARKUP
            )
            return
        
        logger.info(f"Found {len(bookings)} bookings to unbook")
        names = []
        callback_data = []
        bookings['level'] = bookings['level'].astype(int)
        bookings = bookings.sort_values(by=['level', 'timeslot_start_time'])

        for _, booking in bookings.iterrows():

            # Create name for button
            booking_start_str = booking["timeslot_start_time"].strftime("%H:%M")
            booking_end_str = booking["timeslot_end_time"].strftime("%H:%M")
            name = f"Level {booking["level"]} / {booking["timeslot_date"]} / {booking_start_str} - {booking_end_str}"

            # Create name for callback function
            callback = f"unbook_selected_{booking['level']}_{booking['booking_id']}_{booking['timeslot_date']}"
            names.append(name)
            callback_data.append(callback)

        bot.send_message(
            call.message.chat.id,
            "Select a booking to unbook",
            reply_markup=create_markup("UNBOOK SELECT", *create_buttons(names, callback_data))
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('unbook_selected'))
    def unbook(call):
        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Unbooking")
        
        callback_info = call.data.split("_")
        level = callback_info[-3]
        booking_id = callback_info[-2]
        
        # Fetch the booking date (assuming the booking date is passed or fetched from the database)
        booking_date_str = callback_info[-1]  # Assuming the date is passed as 'YYYY-MM-DD'
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()

        result = cancel_booking(level, booking_id)
        if isinstance(result, Exception):
            logger.info(f"Failed to unbook booking id: {booking_id}")
            bot.send_message(
                call.message.chat.id,
                "Failed to unbook. Please try again."
            )
        else:
            logger.info(f"Successfully unbooked booking id: {booking_id}")
            bot.send_message(
                call.message.chat.id,
                "Booking successfully unbooked.",
                reply_markup=START_MARKUP
            )

            # Update the group chat
            today = datetime.today().date()
            if booking_date == today:
                response = get_availability_message(booking_date)
                bot.send_message(
                    CHAT_ID,
                    response,
                    message_thread_id=TOPIC_THREAD_ID
                )
