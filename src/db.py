import psycopg2
import logging
from config import DATABASE_URL
from datetime import datetime, timedelta, date
from constants import KEEP_BOOKINGS_DAYS
import pandas as pd

logger = logging.getLogger("db")

def connect_db():
    try:
        logger.info("Connecting to PostgreSQL database...")
        connection = psycopg2.connect(DATABASE_URL, sslmode="require")
        logger.info("Successfully connected to PostgreSQL database.")
        return connection
    except Exception as e:
        logger.error(f"Error while connecting to PostgreSQL database: {e}")
        return None

def execute_query(query: str, *args):

    conn = connect_db()  # Establish connection
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            logger.info("Executing query")
            cursor.execute(query, args)  # Execute the query

            # For INSERT/UPDATE/DELETE, no results are returned, so just commit and return success
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                conn.close()
                logger.info("Successfully executed query")
                return result
            else:
                conn.commit()
                conn.close()
                logger.info("Successfully executed query")
                return True  # Return success for non-SELECT queries

    except Exception as e:
        conn.close()
        logger.error(f"Error executing query: {e}")
        return e

def add_booking(
        level: int, booking_date: date, username: str, first_name: str, user_chat_id: str, 
        timeslot_date: str, timeslot_start_time: str, timeslot_end_time: str
    ):
    """
    Add booking to level table
    """
    logger.info("Adding booking")
    try:
        # Convert the date from DD/MM/YYYY to YYYY-MM-DD format
        timeslot_date = datetime.strptime(timeslot_date, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if the date format is incorrect
    
    query = f"""
    INSERT INTO level_{level} (booking_datetime, username, first_name, user_chat_id, timeslot_date, timeslot_start_time, timeslot_end_time, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, 'booked')
    """ 
    logger.info(f"Adding booking into level_{level}")
    result = execute_query(query, booking_date, username, first_name, user_chat_id, timeslot_date, timeslot_start_time, timeslot_end_time)

    if isinstance(result, Exception):
        logger.error(f"Error adding booking: {result}")
        return False
    
    return True

def get_bookings_by_date(timeslot_date):
    """
    Fetch bookings from level_9, level_10, and level_11 where timeslot_date matches.
    Returns a Pandas DataFrame containing all matching bookings.
    """

    logger.info("Getting bookings by date")

    if not isinstance(timeslot_date, date):
        try:
            # Convert the date from DD/MM/YYYY to YYYY-MM-DD format
            timeslot_date = datetime.strptime(timeslot_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(f"Invalid date format: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if the date format is incorrect


    # Construct the SQL query to fetch bookings from all levels
    query = """
    SELECT '9' AS level, booking_id, booking_datetime, username, first_name, user_chat_id, timeslot_date, timeslot_start_time, timeslot_end_time, status
    FROM level_9
    WHERE 
        timeslot_date = %s AND
        status = %s

    UNION ALL

    SELECT '10' AS level, booking_id, booking_datetime, username, first_name, user_chat_id, timeslot_date, timeslot_start_time, timeslot_end_time, status
    FROM level_10
    WHERE 
        timeslot_date = %s AND
        status = %s

    UNION ALL

    SELECT '11' AS level, booking_id, booking_datetime, username, first_name, user_chat_id, timeslot_date, timeslot_start_time, timeslot_end_time, status
    FROM level_11
    WHERE 
        timeslot_date = %s AND
        status = %s;
    """
    
    # Execute the query with timeslot_date as the parameter for each level
    result = execute_query(query, timeslot_date, "booked", timeslot_date, "booked", timeslot_date, "booked")

    # Return an empty DataFrame in case of error
    if isinstance(result, Exception):
        logger.error("Error retrieving all bookings")
        return pd.DataFrame()
    
    # Convert the result into a Pandas DataFrame
    columns = ['level', 'booking_id', 'booking_datetime', 'username', 'first_name', 'user_chat_id', 'timeslot_date', 'timeslot_start_time', 'timeslot_end_time', 'status']
    bookings_df = pd.DataFrame(result, columns=columns)

    logger.info(f"Successfully retrieved bookings for {timeslot_date}")
    
    return bookings_df

def get_bookings_by_id(id):

    logger.info("Getting bookings by id")

    # Construct the SQL query to fetch bookings by user chat id
    query = """
    SELECT '9' AS level, booking_id, booking_datetime, username, first_name, user_chat_id, timeslot_date, timeslot_start_time, timeslot_end_time, status
    FROM level_9
    WHERE 
        user_chat_id = %s AND
        status = %s

    UNION ALL

    SELECT '10' AS level, booking_id, booking_datetime, username, first_name, user_chat_id, timeslot_date, timeslot_start_time, timeslot_end_time, status
    FROM level_10
    WHERE 
        user_chat_id = %s AND
        status = %s

    UNION ALL

    SELECT '11' AS level, booking_id, booking_datetime, username, first_name, user_chat_id, timeslot_date, timeslot_start_time, timeslot_end_time, status
    FROM level_11
    WHERE 
        user_chat_id = %s AND
        status = %s;
    """

    # Execute the query with timeslot_date as the parameter for each level
    result = execute_query(query, id, "booked", id, "booked", id, "booked")

    # Return an empty DataFrame in case of error
    if isinstance(result, Exception):
        logger.error("Error retrieving all bookings")
        return pd.DataFrame()
    
    # Convert the result into a Pandas DataFrame
    columns = ['level', 'booking_id', 'booking_datetime', 'username', 'first_name', 'user_chat_id', 'timeslot_date', 'timeslot_start_time', 'timeslot_end_time', 'status']
    bookings_df = pd.DataFrame(result, columns=columns)

    logger.info(f"Successfully retrieved bookings for {id}")

    return bookings_df

def cancel_booking(level: int, booking_id: str):
    """
    Cancel booking by changing booking status of booking_id
    """
    logger.info(f"Cancelling booking id: {booking_id}")

    query = f"""
    UPDATE level_{level}
    SET status = 'cancelled'
    WHERE booking_id = %s
    """ 

    logger.info(f"Updating status of booking from level_{level} to 'cancelled'")
    result = execute_query(query, booking_id)

    if isinstance(result, Exception):
        logger.error(f"Error cancelling booking id: {booking_id}")
    else:
        logger.info(f"Successfully updated booking id: {booking_id} to 'cancelled'")

def clear_old_bookings():
    conn = connect_db()  # Establish connection
    if conn is None:
        return
    
    logger.info("Clearing all bookings")

    try:
        with conn.cursor() as cursor:
            # Calculate the date before which data should be deleted
            cutoff_date = datetime.now() - timedelta(days=KEEP_BOOKINGS_DAYS)
            
            # Convert cutoff_date to a string suitable for SQL query
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

            # SQL query to delete bookings older than the cutoff date
            for level in range(9, 12):

                query = f"""
                DELETE FROM level_{level}
                WHERE booking_datetime < %s
                """
                
                logger.info(f"Deleting bookings from level_{level} older than {KEEP_BOOKINGS_DAYS} days.")

                cursor.execute(query, (cutoff_date_str,))
                rows_deleted = cursor.rowcount
                conn.commit()  # Commit the deletion

                logger.info(f"Deleted {rows_deleted} bookings from level_{level} older than {KEEP_BOOKINGS_DAYS} days.")

    except Exception as e:
        logger.error(f"Error clearing old bookings from level_{level}: {e}")
    finally:
        conn.close()  # Close the connection after use

def update_booking(level: int, booking_id: str, new_start_time: str, new_end_time: str):
    """
    Update booking by changing the start and end time for a booking with the given booking_id.
    """
    logger.info(f"Updating booking id: {booking_id} for level: {level}")

    query = f"""
    UPDATE level_{level}
    SET 
        timeslot_start_time = %s, 
        timeslot_end_time = %s, 
        booking_datetime = NOW()
    WHERE booking_id = %s
    """ 

    logger.info(f"Updating start and end times for booking id {booking_id} in level_{level}")
    result = execute_query(query, new_start_time, new_end_time, booking_id)

    if isinstance(result, Exception):
        logger.error(f"Error updating booking id: {booking_id}")
        return False
    else:
        logger.info(f"Successfully updated booking id: {booking_id}")
        return True
