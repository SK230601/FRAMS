import mysql.connector;
from datetime import datetime;
import calendar

from user import User;

def get_database_connection():
    # Return a connection and cursor to the database
    return mysql.connector.connect(host="localhost", user="root", password="root@123", database="attendace_py")

def generate_new_user(user_id, password, fname, lname, wages, image_name):

    conn = get_database_connection()
    cursor = conn.cursor()

    # # Create a table
    # create_table_query = """
    #     CREATE TABLE IF NOT EXISTS users_table (
    #         user_id INT PRIMARY KEY,
    #         type VARCHAR(10) NOT NULL
    #         fname VARCHAR(30) NOT NULL,
    #         lname VARCHAR(30) NOT NULL,
    #         password VARCHAR(15) NOT NUll,
    #         image_name VARCHAR(50) NOT NULL,
    #         wages_hr INT NOT NULL,
    #         status VARCHAR(10)
    #     )
    #     """
    # cursor.execute(create_table_query)

    insert_data_query = """
        INSERT INTO users_table (user_id, type, fname, lname, password, image_name, wages_hr, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    # insert data andexecute query
    user_data = (user_id, "User", fname, lname, password, image_name, 0, "Pending")
    cursor.execute(insert_data_query, user_data)

    # Commit the changes to the database
    conn.commit()

    # Closing the connection
    cursor.close()
    conn.close() 

    return user_id

# generate_new_user()

def get_all_breaks(user_id):
    
    conn = get_database_connection()
    cursor = conn.cursor()

    # query for fetching all records
    get_query_for_users = "SELECT * from breaks where user_id = %s"
    cursor.execute(get_query_for_users,(user_id,))
    breaks = cursor.fetchall()

    # Closing the connection
    cursor.close()
    conn.close() 

    return breaks

def get_all_users():
    conn = get_database_connection()
    cursor = conn.cursor()

    # query for fetching all records
    get_query_for_users = "SELECT * FROM users_table"
    cursor.execute(get_query_for_users)
    users_data = cursor.fetchall()

    # Convert data into list of User objects
    users = []
    for user_data in users_data:
        user_id, type, fname, lname, password, image_name, wages_hr, status = user_data
        user = User(user_id, type, fname, lname, password, image_name, wages_hr, status)
        users.append(user)

    # Closing the connection
    cursor.close()
    conn.close()

    return users

def get_all_users_with_pending_status():
    conn = get_database_connection()
    cursor = conn.cursor()

    # query for fetching all records
    get_query_for_users = "SELECT * FROM users_table WHERE status = 'Pending'"
    cursor.execute(get_query_for_users)
    users_records = cursor.fetchall()

    # Closing the connection
    cursor.close()
    conn.close()

    return users_records

def get_all_attendance_records():
    
    conn = get_database_connection()
    cursor = conn.cursor()

    # query for fetching all records
    get_query_for_recorde = "SELECT * from attendance"
    cursor.execute(get_query_for_recorde)
    records = cursor.fetchall()

    # Closing the connection
    cursor.close()
    conn.close() 

    return records

def get_all_break_records(userid):
    
    conn = get_database_connection()
    cursor = conn.cursor()

    # query for fetching all records
    get_query_for_records = "SELECT * from breaks where user_id = %s"
    cursor.execute(get_query_for_records, (userid,))
    records = cursor.fetchall()

    # Closing the connection
    cursor.close()
    conn.close() 

    return records

def get_all_entries_by_user_id(user_id):

    conn = get_database_connection()
    cursor = conn.cursor()

    # query for fetching all records of one user
    get_query_for_entries = "SELECT * from attendance where user_id = %s"
    cursor.execute(get_query_for_entries,(user_id,))
    users = cursor.fetchall()

    # Closing the connection
    cursor.close()
    conn.close() 

    return users

def get_records_between_dates(user_id, sdate, edate):
    # database connection code
    conn = get_database_connection()
    cursor = conn.cursor()

    # taking data for perticular name and dates between
    select_query = "SELECT * FROM attendance where user_id = %s and date between %s and %s"
    cursor.execute(select_query, (user_id, sdate, edate))
    records = cursor.fetchall()

    # Closing the connection
    cursor.close()
    conn.close() 

    return records
    
def calculate_monthly_salary_breaks(month, year):

    # database connection code
    conn = get_database_connection()
    cursor = conn.cursor()

    # Check if year and month are not None and are valid integers
    if year is not None and month is not None and year.isdigit() and month.isdigit():
        year = int(year)
        month = int(month)

        # taking data for perticular name and dates between
        start_date = datetime(year, month, 1).strftime("%Y-%m-%d")
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day).strftime("%Y-%m-%d")
    
        salaries = []
        # list of employees from database
        get_employees = "SELECT distinct user_id from attendance"
        cursor.execute(get_employees)
        employees = cursor.fetchall()

        for employee in employees:
            user_id = employee[0]

            # taking data for perticular name and dates between
            select_query = "SELECT user_id, name, hrs_worked FROM attendance where user_id = %s and date between %s and %s"
            cursor.execute(select_query, (user_id, start_date, end_date))
            records = cursor.fetchall()

            total_working_hours = 0

            for record in records:

                hrs_worked = float(record[2])
                total_working_hours += hrs_worked
                # in_time = datetime.strptime(str(record[1]), '%H:%M:%S')
                # out_time = datetime.strptime(str(record[2]), '%H:%M:%S')

                # # calculating the time diffrence
                # if in_time and out_time:
                #     working_hrs = out_time - in_time
                #     total_working_hours += (working_hrs.total_seconds() / 3600)

            # taking data for perticular name and dates between for approved breaks
            select_query1 = "SELECT user_id, name, break_hrs FROM claims where user_id = %s and claim_status = 'Approved' and date between %s and %s"
            cursor.execute(select_query1, (user_id, start_date, end_date))
            breaks = cursor.fetchall()

            for b in breaks:

                brk_worked = float(b[2])
                total_working_hours += brk_worked

            # taking Hourly Wages from user table
            query_wages = "SELECT fname, lname, wages_hr from users_table where user_id = %s"
            cursor.execute(query_wages, (user_id,))
            wagesE = cursor.fetchone()

            # Calculating salary per month
            if wagesE:
                name = wagesE[0] + wagesE[1]
                wages = wagesE[2]
                salary = wages * total_working_hours
            else:
                print(f"No wages found for user_id: {user_id}")

            salaries.append((user_id, name, total_working_hours, wages, salary))

        cursor.close()
        conn.close() 

        return salaries
    
    else:
        # Handle the case where year or month is None or not valid integers
        return "Error"
    
def application_approve(data):

    conn = get_database_connection()
    cursor = conn.cursor()

    # Retrieving data by keys
    user_id = data['user_id']
    password = data['password']
    wages_hr = int(data['wages_hr'])

    # query for updating data in database claims table
    query_update = "UPDATE users_table SET status = %s, wages_hr = %s where user_id = %s and password = %s"
    cursor.execute(query_update, ("Approved", wages_hr, user_id, password))
    conn.commit()

    # Closing the connection
    cursor.close()
    conn.close() 

def application_reject(data):

    conn = get_database_connection()
    cursor = conn.cursor()

    # Retrieving data by keys
    user_id = data['user_id']
    password = data['password']
    wages_hr = int(data['wages_hr'])

    # query for updating data in database claims table
    query_update = "UPDATE users_table SET status = %s, wages_hr = %s where user_id = %s and password = %s"
    cursor.execute(query_update, ("Rejected", wages_hr, user_id, password))
    conn.commit()

    # Closing the connection
    cursor.close()
    conn.close() 
