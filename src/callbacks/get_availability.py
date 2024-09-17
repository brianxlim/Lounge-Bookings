import logging
from callbacks.back import callback_back
from constants import START_MARKUP, GET_MARKUP, WELCOME_MESSAGE, TZ_DIFF_HOURS
from db import get_bookings_by_date
from datetime import datetime, timedelta

logger = logging.getLogger('callback (get)')

def callback_get_availability(bot):
    callback_back(bot)(WELCOME_MESSAGE, START_MARKUP, "Get Availability")

    @bot.callback_query_handler(func=lambda call: call.data == 'get_availability_select_date')
    def select_date(call):

        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Checking Availability")
        
        bot.send_message(
            call.message.chat.id,
            "Which dates would you like to check?",
            reply_markup=GET_MARKUP
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('get_availability_date_selected'))
    def get_availability(call):
        
        logger.info(f"{call.from_user.first_name} (@{call.from_user.username}) Checking Availability")
        logger.info(call.data)
        
        date = call.data.split("+")[1]
        response = get_availability_message(date)

        bot.send_message(
            call.message.chat.id,
            response
        )

# Helper function for get_availability callback – abstracted to use in booking and unbooking
def get_availability_message(date):
        bookings = get_bookings_by_date(date)

        response = f"Lounge Bookings for {date}:\n"
        if bookings.empty:
            response += "\nAll lounges are unbooked!"

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
                        booking_time = row['booking_datetime']
                        booking_time += timedelta(hours=TZ_DIFF_HOURS)
                        booking_time = datetime.now() - booking_time
                        booking_time = booking_time.seconds
                        booking_time = "seconds" if booking_time < 60 else f"{round(booking_time / 60)} mins" if booking_time < 3600 else f"{round(booking_time / 3600)} hrs" if booking_time < 86400 else f"{round(booking_time / 86400)} days"
                        
                        # Add booking details with bullet point
                        response += f"• {start_time} - {end_time} by {first_name} (@{username}), {booking_time} ago\n"
        
        return response