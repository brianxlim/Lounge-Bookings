def create_tables_query():
    query = """
    CREATE TABLE bookings (
        booking_id SERIAL PRIMARY KEY,
        booking_datetime TIMESTAMP NOT NULL,
        level INT NOT NULL,
        username VARCHAR(255),
        first_name VARCHAR(255),
        user_chat_id BIGINT NOT NULL,
        timeslot_date DATE NOT NULL,
        timeslot_start_time TIME NOT NULL,
        timeslot_end_time TIME NOT NULL,
        status VARCHAR(50)
    );
    """
    return query

def drop_table_query():
    return "DROP TABLE IF EXISTS bookings;"

def add_booking_query():
    query = f"""
    INSERT INTO bookings (
        level,
        booking_datetime,
        username,
        first_name,
        user_chat_id,
        timeslot_date,
        timeslot_start_time,
        timeslot_end_time,
        status
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """ 
    return query

def get_all_bookings_query():
    query = """
    SELECT * 
    FROM bookings 
    WHERE timeslot_date >= %s;
    """
    return query

def get_bookings_by_date_query():
    query = """
    SELECT * 
    FROM bookings
    WHERE 
        timeslot_date = %s AND
        status = %s;
    """
    return query

def get_bookings_by_id_query():
    query = """
    SELECT *
    FROM bookings
    WHERE 
        user_chat_id = %s AND
        status = %s;
    """
    return query

def cancel_booking_query():
    query = """
    UPDATE bookings
    SET status = 'cancelled'
    WHERE booking_id = %s
    """ 
    return query