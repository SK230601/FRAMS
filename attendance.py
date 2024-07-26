from datetime import datetime, timedelta;
import mysql.connector;
from mysql.connector import Error

def get_database_connection():
    # Return a connection and cursor to the database
    return mysql.connector.connect(host="localhost",
        user="root",
        password="root@123",
        database="attendace_py")

def markCheckInAttendances(user_id, name):

    # database connection code
    conn = get_database_connection()
    cursor = conn.cursor()

    # Create a table
    # create_table_query = """
    #     CREATE TABLE IF NOT EXISTS attendance (
    #         user_id INT primary key,
    #         name VARCHAR(30) NOT NULL,
    #         date DATE NOT NULL,
    #         in_time TIME,
    #         out_time TIME,
    #         hrs_worked Float,
    #         status VARCHAR(1)
    #     )
    #     """
    # cursor.execute(create_table_query)

    # Check if the userId already exists in the database
    query_check = "SELECT * FROM attendance WHERE user_id = %s and date = %s"
    now_date = datetime.now().strftime('%Y-%m-%d')

    cursor.execute(query_check, (user_id, now_date))
    existing_record = cursor.fetchone()

    now = datetime.now()
    time = now.strftime('%H:%M:%S')
    date = now.strftime('%Y-%m-%d')

    if not existing_record:
        # Insert a new record if the userId is not found
        now = datetime.now()
        time = now.strftime('%H:%M:%S')
        date = now.strftime('%Y-%m-%d')

        # Insert the new record into the database
        query_insert = "INSERT INTO attendance (user_id, name, date, in_time, out_time, hrs_worked, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query_insert, (user_id, name, date, time, "", 0, "A"))

        # Commit the changes
        conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return time, date

def markCheckOutAttendances(user_id, name):
    # Connect to your MySQL database
    conn = get_database_connection()
    cursor = conn.cursor()

    # Create a table
    # create_table_query = """
    #     CREATE TABLE IF NOT EXISTS attendance (
    #         user_id INT Not Null,
    #         name VARCHAR(255) NOT Null,
    #         date DATE NOT NULL,
    #         in_time TIME,
    #         out_time TIME,
    #         break_out TIME,

    #         hrs_worked DECIMAL(10,2),
    #         status VARCHAR(7)
    #     )
    # """
    # cursor.execute(create_table_query)

    # getting date and time for checkout entry
    now = datetime.now()
    # time = now.strftime('%H:%M:%S')
    time = now.time()
    date = now.strftime('%Y-%m-%d')

    # check outtime is not marked by using date userId and name from database
    get_employee = "SELECT status from attendance where user_id = %s and name = %s and date = %s and in_time IS NOT NULL"
    cursor.execute(get_employee, (user_id, name, date))
    status = cursor.fetchone()

    if status[0] == "A":
        # get employee by date userId and name from database
        get_employee = "SELECT in_time from attendance where user_id = %s and name = %s and date = %s and in_time IS NOT NULL"
        cursor.execute(get_employee, (user_id, name, date))
        in_timed = cursor.fetchone()

        now_time  = datetime.combine(datetime(1900, 1, 1), time)
        in_time = datetime.strptime(str(in_timed[0]), '%H:%M:%S')

        breaks_query = "Select break_hrs from breaks where user_id = %s and date = %s"
        cursor.execute(breaks_query,(user_id,date))
        break_user = cursor.fetchall()

        total_break_time = 0
        for b in break_user:
            total_break_time += float(b[0])

        # Convert total_break_time to float
        total_break_time = float(total_break_time)

        # calculating total working hours
        total_working_hours = 0
        if in_time and time:
            working_hrs = now_time - in_time
            total_working_hours = (working_hrs.total_seconds() / 3600)

        # Subtract total_break_time from total_working_hours
        total_working_hours = total_working_hours - total_break_time

        # Update the time for a specific entry
        update_query = "UPDATE attendance SET out_time = %s, status = %s, hrs_worked = %s WHERE user_id = %s and name = %s and date = %s and in_time IS NOT NULL"
        cursor.execute(update_query, (time, "P", total_working_hours, user_id, name, date))

    # Commit the changes, Close the cursor and connection
    conn.commit()
    cursor.close()
    conn.close()

    now1 = datetime.now()
    time1 = now1.strftime('%H:%M:%S')
    date1 = now1.strftime('%Y-%m-%d')

    return time1, date1

# Function to mark breakouts and breakins in the database
def markBreakOut(user_id, name):

    now = datetime.now()
    time = now.strftime('%H:%M:%S')
    date = now.strftime('%Y-%m-%d')

    connection = get_database_connection()
    cusrsor = connection.cursor()

    query = "SELECT COUNT(*) FROM breaks WHERE user_id = %s AND date = %s"
    cusrsor.execute(query, (user_id, date))
    entryC = cusrsor.fetchone()[0]


    if entryC == 0:

        query_insert = "INSERT INTO breaks (user_id, name, date, break_out, break_in, break_hrs, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cusrsor.execute(query_insert, (user_id, name, date, time, "", 0, "N"))
        connection.commit()

    elif entryC == 1:

        query_emp = "SELECT * FROM breaks WHERE user_id = %s AND date = %s"
        cusrsor.execute(query_emp, (user_id, date))
        entry = cusrsor.fetchone()

        break_out_time = entry[3]  # Assuming entry[3] represents the break_out time as a timedelta object
        time_difference = now - (now.replace(hour=break_out_time.seconds // 3600, minute=(break_out_time.seconds // 60) % 60, second=break_out_time.seconds % 60))

        if entry[6] == "N" and (time_difference >= timedelta(minutes=3)):

            break_hrs = time_difference.total_seconds() / 3600
            update_query = "UPDATE breaks SET break_in = %s, status = %s, break_hrs = %s WHERE user_id = %s AND date = %s"
            cusrsor.execute(update_query, (time, "T", break_hrs, user_id, date))
            connection.commit()

        elif entry[6] == "T":

            in_time = entry[4]
            diff = now - (now.replace(hour=in_time.seconds // 3600, minute=(in_time.seconds // 60) % 60, second=in_time.seconds % 60))

            if(diff >= timedelta(minutes=1)):

                insert = "INSERT INTO breaks (user_id, name, date, break_out, break_in, break_hrs, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cusrsor.execute(insert, (user_id, name, date, time, "", 0, "N"))
                connection.commit()

    elif(entryC == 2):

        query_emp = "SELECT * FROM breaks WHERE user_id = %s AND date = %s AND status = %s"
        status = "N"
        cusrsor.execute(query_emp, (user_id, date, status))
        entry = cusrsor.fetchone()
        print(entry)

        try:
            bout_time = entry[3]  # Assuming entry[3] represents the break_out time as a timedelta object
            difference = now - (now.replace(hour=bout_time.seconds // 3600, minute=(bout_time.seconds // 60) % 60, second=bout_time.seconds % 60))

            if entry[6] == "N" and (difference >= timedelta(minutes=2)):

                break_hrs = difference.total_seconds() / 3600
                update_query = "UPDATE breaks SET break_in = %s, status = %s, break_hrs = %s WHERE user_id = %s AND date = %s AND status = %s"
                cusrsor.execute(update_query, (time, "T", break_hrs, user_id, date, "N"))
                connection.commit()
                
        except TypeError:
            pass

    else:
        print("Entries Exceeded .............")

    cusrsor.close()
    connection.close() 

# def markBreakOut(user_id, name):
#     now = datetime.now()
#     time = now.strftime('%H:%M:%S')
#     date = now.strftime('%Y-%m-%d')
#     time_before_3min = now - timedelta(minutes=3)

#     # Required Queries
#     query_insert = "INSERT INTO breaks (user_id, name, date, break_out, break_in, break_hrs, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
#     latest_query = "SELECT * FROM breaks WHERE user_id = %s AND date = %s ORDER BY break_out DESC LIMIT 1"
#     get_employee = "SELECT break_out FROM breaks WHERE user_id = %s AND name = %s AND date = %s AND break_out IS NOT NULL"
#     update_query = "UPDATE breaks SET break_in = %s, status = %s, break_hrs = %s WHERE user_id = %s AND name = %s AND date = %s AND break_out IS NOT NULL"
    

#     # Connect to your MySQL database
#     conn = get_database_connection()
#     cursor = conn.cursor()

#     # Count the existing entries for the user on the given date
#     count_query = "SELECT COUNT(*) FROM breaks WHERE user_id = %s AND date = %s"
#     cursor.execute(count_query, (user_id, date))
#     entry_count = cursor.fetchone()[0]

#     if entry_count == 0:
#             # Insert the new record into the database
#             cursor.execute(query_insert, (user_id, name, date, time, "", 0, "N"))
#             conn.commit()

#     elif entry_count == 1:
#             # Fetch the latest entry for the user on the given date
#             cursor.execute(latest_query, (user_id, date))
#             latest_entry = cursor.fetchone()

#             if latest_entry[6] == "N":
#                 emp_3_datetime = now - latest_entry[3]
#                 if emp_3_datetime < time_before_3min:
#                     cursor.execute(get_employee, (user_id, name, date))
#                     out = cursor.fetchone()
#                     break_outact = datetime.strptime(str(out[0]), '%H:%M:%S')

#                     total_break_hours = 0
#                     now_obj_time = datetime.strptime(time, '%H:%M:%S')

#                     if break_outact and time:
#                         break_hrs = now_obj_time - break_outact
#                         total_break_hours = (break_hrs.total_seconds() / 3600)

#                     cursor.execute(update_query, (time, "T", total_break_hours, user_id, name, date))
#                     conn.commit()

#             elif latest_entry[6] == "T":
#                 emp_in_time = now - latest_entry[4]
#                 if emp_in_time < time_before_3min:
#                     cursor.execute(query_insert, (user_id, name, date, time, "", 0, "N"))
#                     conn.commit()

#     elif entry_count == 2:
#             cursor.execute(latest_query, (user_id, date))
#             latest_entry = cursor.fetchone()

#             if latest_entry[6] == "N":
#                 emp_3_datetime = now - latest_entry[3]
#                 if emp_3_datetime < time_before_3min:
#                     cursor.execute(get_employee, (user_id, name, date))
#                     out = cursor.fetchone()
#                     break_outact = datetime.strptime(str(out[0]), '%H:%M:%S')

#                     total_break_hours = 0
#                     now_obj_time = datetime.strptime(time, '%H:%M:%S')

#                     if break_outact and time:
#                         break_hrs = now_obj_time - break_outact
#                         total_break_hours = (break_hrs.total_seconds() / 3600)

#                     cursor.execute(update_query, (time, "T", total_break_hours, user_id, name, date))
#                     conn.commit()

#             elif latest_entry[6] == "T":
#                 print("Maximum 2 entries reached for the day")

#     else:
#         print("Maximum entries reached for the day")

#     cursor.close()
#     conn.close()

