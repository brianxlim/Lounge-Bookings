import logging
from callbacks.back import callback_back
from constants import START_MARKUP, GET_MARKUP, WELCOME_MESSAGE, UTC_DIFF_HOURS
from db import get_bookings_by_date, get_all_bookings
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger('callback (get)')

def callback_get_availability(bot):
    callback_back(bot)(WELCOME_MESSAGE, START_MARKUP, "Get Availability")

    @bot.callback_query_handler(func=lambda call: call.data == 'get_availability_select_date')
    def select_date(call):

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Checking Availability")
        
        bot.send_message(
            call.message.chat.id,
            "Which dates would you like to check?",
            reply_markup=GET_MARKUP
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('get_availability_date_selected'))
    def get_availability(call):

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        
        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Checking Availability")

        date = call.data.split("+")[1]

        logger.info(f"Checking {date} availability")

        response = get_availability_message(date)

        bot.send_message(
            call.message.chat.id,
            response,
            reply_markup=START_MARKUP
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('get_availability_all_selected'))
    def get_availability_all(call):

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

        logger.info("Checking all availability")

        response = ""
        bookings = get_all_bookings()
        bookings = bookings.sort_values(by=["timeslot_date", "level", "timeslot_start_time"])

        # Define the date range you want to check (e.g., the next 7 days)
        today_sgt = datetime.now(ZoneInfo("Asia/Singapore")).date()
        date_range = [today_sgt + timedelta(days=i) for i in range(7)]
        
        # Iterate over each date in the date range
        for date in date_range:
            # Filter bookings for the current date
            bookings_for_date = bookings[bookings["timeslot_date"] == date]
            
            if bookings_for_date.empty:
                # No bookings for this date, so mark all lounges as unbooked
                response += f"Lounge bookings for {date.strftime("%d/%m/%Y")}:\nAll lounges are unbooked!\n\n"
            else:
                # There are bookings, so group by level and list the bookings
                response += f"Lounge bookings for {date.strftime("%d/%m/%Y")}:\n"
                for level, level_group in bookings_for_date.groupby("level"):
                    prefix = "\U0001F467\U0001F467" if level == '9' else "\U0001F466\U0001F466" if level == "10" else "\U0001F466\U0001F467"
                    response += f"\n{prefix} Level {level} {prefix}\n"
                    for _, row in level_group.iterrows():
                        start_time = row["timeslot_start_time"].strftime("%H:%M")
                        end_time = row["timeslot_end_time"].strftime("%H:%M")

                        # Find time booked
                        booking_time = row['booking_datetime'].replace(tzinfo=ZoneInfo('UTC'))
                        booking_time = datetime.now(ZoneInfo('UTC')) - booking_time
                        booking_time += timedelta(hours=UTC_DIFF_HOURS)
                        booking_time = booking_time.seconds
                        booking_time = "seconds" if booking_time < 60 else f"{round(booking_time / 60)} mins" if booking_time < 3600 else f"{round(booking_time / 3600)} hrs" if booking_time < 86400 else f"{round(booking_time / 86400)} days"

                        response += f"• {start_time} - {end_time} by {row['first_name']} (@{row['username']}) {booking_time} ago\n"
                response += "\n"  # Add a newline between different timeslot_date blocks

        # Send the message with the response
        bot.send_message(
            call.message.chat.id,
            response,
            reply_markup=START_MARKUP
        )
        
# Helper function for get_availability callback – abstracted to use in booking and unbooking
def get_availability_message(date):
        bookings = get_bookings_by_date(date)

        response = f"Lounge Bookings for {date}:\n"
        if bookings.empty:
            response += "\nAll lounges are unbooked!\n"

        else:
            # Group bookings by level
            for level in ['9', '10', '11']:
                level_bookings = bookings[bookings['level'] == level]
                level_bookings = level_bookings.sort_values(by='timeslot_start_time')
                
                if not level_bookings.empty:
                    # Add the level header
                    prefix = "\U0001F467\U0001F467" if level == '9' else "\U0001F466\U0001F466" if level == "10" else "\U0001F466\U0001F467"
                    response += f"\n{prefix} Level {level} {prefix}\n"
                    
                    # Add each booking in the level
                    for _, row in level_bookings.iterrows():
                        start_time = row['timeslot_start_time'].strftime('%H:%M')
                        end_time = row['timeslot_end_time'].strftime('%H:%M')
                        first_name = row['first_name']
                        username = row['username']

                        # Find time booked
                        booking_time = row['booking_datetime'].replace(tzinfo=ZoneInfo('UTC'))
                        booking_time = datetime.now(ZoneInfo('UTC')) - booking_time
                        booking_time += timedelta(hours=UTC_DIFF_HOURS)
                        booking_time = booking_time.seconds
                        booking_time = "seconds" if booking_time < 60 else f"{round(booking_time / 60)} mins" if booking_time < 3600 else f"{round(booking_time / 3600)} hrs" if booking_time < 86400 else f"{round(booking_time / 86400)} days"
                        
                        # Add booking details with bullet pointb
                        response += f"• {start_time} - {end_time} by {first_name} (@{username}), {booking_time} ago\n"
        
        return response