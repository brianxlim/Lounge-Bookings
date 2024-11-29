import atexit
import psycopg2
from constants import KEEP_BOOKINGS_DAYS, UTC_DIFF_HOURS, COLUMNS
from config import DATABASE_URL
from datetime import datetime, timedelta, date
import logging
import pandas as pd
from .query import drop_table_query, create_tables_query, add_booking_query, get_all_bookings_query, get_bookings_by_date_query, get_bookings_by_id_query, cancel_booking_query
from zoneinfo import ZoneInfo

logger = logging.getLogger("db")

class DatabaseHandler:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None
        self.connect()

    def drop_table(self):
        logger.info("Dropping tables")
        self.execute_query(drop_table_query())

    def connect(self):
        if self.connection is None or self.connection.closed != 0:
            try:
                logger.info("Connecting to PostgreSQL database...")
                self.connection = psycopg2.connect(self.db_url)
                logger.info("Successfully connected to PostgreSQL database.")

            except Exception as e:
                logger.error(f"Error while connecting to PostgreSQL database: {e}")
                self.connection = None
        return self.connection
    
    def create_table(self):
        self.execute_query(create_tables_query())
    
    def get_table_schema(self, table_name):
        query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s;
        """
        result = self.execute_query(query, table_name)
        if isinstance(result, Exception):
            logger.error(f"Error fetching schema for table '{table_name}': {result}")
            return None
        else:
            logger.info(f"Schema for table '{table_name}':")
            for row in result:
                logger.info(f"Column: {row[0]}, Type: {row[1]}")
            return result

    def execute_query(self, query, *args):
        conn = self.connect()
        if conn is None:
            return None

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, args)

                if query.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                    logger.info("Successfully executed query")
                    return result
                else:
                    conn.commit()
                    logger.info(f"Successfully executed query: {query}")
                    return True
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return e
    
    def clear_old_bookings(self):
        conn = self.connect()
        if conn is None:
            logger.error("Failed to connect to the database to clear old bookings")
            return 

        try:
            with conn.cursor() as cursor:
                # Calculate the date before which data should be deleted
                cutoff_date = datetime.now(ZoneInfo('utc')) + timedelta(hours=UTC_DIFF_HOURS) - timedelta(days=KEEP_BOOKINGS_DAYS)
                cutoff_date_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

                # SQL query to delete bookings older than the cutoff date
                query = """
                DELETE FROM bookings
                WHERE booking_datetime < %s
                """
                
                logger.info(f"Deleting bookings older than {KEEP_BOOKINGS_DAYS} days from 'bookings' table.")

                cursor.execute(query, (cutoff_date_str,))
                rows_deleted = cursor.rowcount
                conn.commit()  # Commit the deletion

                logger.info(f"Deleted {rows_deleted} bookings older than {KEEP_BOOKINGS_DAYS} days from 'bookings' table.")

        except Exception as e:
            logger.error(f"Error clearing old bookings: {e}")

    def close(self):
        if self.connection and self.connection.closed == 0:
            self.connection.close()
            logger.info("Closed PostgreSQL connection.")

db_handler = DatabaseHandler(DATABASE_URL)

def add_booking(
        level: int, booking_date: date, username: str, first_name: str, user_chat_id: str,
        timeslot_date: str, timeslot_start_time: str, timeslot_end_time: str
    ):
    """
    Add booking
    """
    logger.info("Adding booking")

    try:
        timeslot_date = datetime.strptime(timeslot_date, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        return pd.DataFrame()  # Return empty DataFrame

    result = db_handler.execute_query(add_booking_query(), level, booking_date, username, first_name, user_chat_id, timeslot_date, timeslot_start_time, timeslot_end_time, "booked")

    if isinstance(result, Exception):
        logger.error(f"Error adding booking: {result}")
        return False
    
    return True

def get_all_bookings():
    """
    Fetch all bookings for coming week
    """
    logger.info(f"Getting all bookings")

    today = datetime.today() + timedelta(hours=UTC_DIFF_HOURS)
    today_str = today.date().strftime('%Y-%m-%d')  # Convert to YYYY-MM-DD format

    # Use parameterized query
    result = db_handler.execute_query(get_all_bookings_query(), today_str)

    if isinstance(result, Exception):
        logger.error("Error retrieving all bookings")
        return pd.DataFrame()

    bookings_df = pd.DataFrame(result, columns=COLUMNS)

    logger.info("Successfully retrieved all bookings")

    return bookings_df

def get_bookings_by_date(timeslot_date):
    """
    Fetch bookings where timeslot_date matches.
    Returns a Pandas DataFrame containing all matching bookings.
    """
    logger.info("Getting bookings by date")

    if not isinstance(timeslot_date, date):
        try:
            # Convert the date from DD/MM/YYYY to YYYY-MM-DD format
            timeslot_date = datetime.strptime(timeslot_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(f"Invalid date format: {e}")
            return pd.DataFrame()  # Return an empty DataFrame
    
    # Execute the query with timeslot_date as the parameter for each level
    result = db_handler.execute_query(get_bookings_by_date_query(), timeslot_date, "booked")

    # Return an empty DataFrame in case of error
    if isinstance(result, Exception):
        logger.error(f"Error retrieving bookings for {timeslot_date}")
        return pd.DataFrame()
    
    bookings_df = pd.DataFrame(result, columns=COLUMNS)

    logger.info(f"Successfully retrieved bookings for {timeslot_date}")
    return bookings_df

def get_bookings_by_id(id):

    logger.info("Getting bookings by id")

    # Execute the query with timeslot_date as the parameter for each level
    result = db_handler.execute_query(get_bookings_by_id_query(), id, "booked")

    # Return an empty DataFrame in case of error
    if isinstance(result, Exception):
        logger.error("Error retrieving all bookings")
        return pd.DataFrame()
    
    bookings_df = pd.DataFrame(result, columns=COLUMNS)

    logger.info(f"Successfully retrieved bookings for {id}")
    return bookings_df

def cancel_booking(level: int, booking_id: str):
    """
    Cancel booking by changing booking status of booking_id
    """
    logger.info(f"Cancelling booking id: {booking_id}")

    logger.info(f"Updating status of booking from level_{level} to 'cancelled'")
    result = db_handler.execute_query(cancel_booking_query(), booking_id)

    if isinstance(result, Exception):
        logger.error(f"Error cancelling booking id: {booking_id}")
        return False
    else:
        logger.info(f"Successfully updated booking id: {booking_id} to 'cancelled'")
        return True

atexit.register(db_handler.close)
