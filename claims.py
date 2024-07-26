import mysql.connector;
from datetime import datetime;


def get_database_connection():
    return mysql.connector.connect(host="localhost", user="root", password="root@123", database="attendace_py")

def new_claim(data):

    conn = get_database_connection()
    cursor = conn.cursor()

    # print("Inside New claim")
    # Retrieving data by keys
    user_id = data['user_id']
    user_name = data['user_name']
    date = data['date']
    break_out = data['break_out']
    break_in = data['break_in']
    break_hrs = data['break_hrs']
    status = data['status']
    message = data['message']
    # print(message)

    # query for adding data in database claims table
    query_insert = "INSERT INTO claims (user_id, name, date, break_out, break_in, break_hrs, status, message, claim_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query_insert, (user_id, user_name, date, break_out, break_in, break_hrs, status, message, "Pending"))
    conn.commit()

    try:
        hrs = break_hrs
        # Deleting the matching entry from the breaks record
        delete_query = "DELETE FROM breaks WHERE user_id = %s AND date = %s and break_hrs = %s"
        cursor.execute(delete_query, (user_id, date, hrs))
        conn.commit()
    except Exception as e:
        print("Error:", e)


    # Closing the connection
    cursor.close()
    conn.close() 

def get_all_claims():

    conn = get_database_connection()
    cursor = conn.cursor()

    # query for fetching all records
    get_query_for_claims = "SELECT * from claims where claim_status = %s"
    cursor.execute(get_query_for_claims, ('Pending',))
    claims = cursor.fetchall()

    # Closing the connection
    cursor.close()
    conn.close() 

    return claims

def get_entries_by_userid(id):

    conn = get_database_connection()
    cursor = conn.cursor()

    # query for fetching all records
    get_query_for_claims = "SELECT * from claims where user_id = %s"
    cursor.execute(get_query_for_claims, (id,))
    claims = cursor.fetchall()

    # Closing the connection
    cursor.close()
    conn.close() 

    return claims

def claim_approve(data):

    conn = get_database_connection()
    cursor = conn.cursor()

    # Retrieving data by keys
    user_id = data['user_id']
    date = data['date']
    break_out = data['break_out']
    break_hrs = data['break_hrs']
    message = data['message']

    # query for updating data in database claims table
    query_update = "UPDATE claims SET claim_status = %s where user_id = %s and date = %s and break_out = %s and break_hrs = %s And message = %s"
    cursor.execute(query_update, ("Approved", user_id, date, break_out, break_hrs, message))
    conn.commit()

    # # deleting perticular entry from breaks table
    # u_id = int(data['user_id'])
    # b_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    # b_hrs = float(data['break_hrs'])

    # delete_query = "DELETE FROM breaks WHERE user_id = %s AND date = %s AND break_hrs = %s"
    # cursor.execute(delete_query, (u_id, b_date, b_hrs))
    # conn.commit()

    # Closing the connection
    cursor.close()
    conn.close() 

def claim_reject(data):

    conn = get_database_connection()
    cursor = conn.cursor()

    # print(data)

    # Retrieving data by keys
    user_id = data['user_id']
    date = data['date']
    break_out = data['break_out']
    break_hrs = data['break_hrs']
    message = data['message']

    # query for updating data in database claims table
    query_update = "UPDATE claims SET claim_status = %s WHERE user_id = %s AND date = %s AND break_out = %s AND break_hrs = %s And message = %s"
    cursor.execute(query_update, ("Rejected", user_id, date, break_out, break_hrs, message))
    conn.commit()

    # Closing the connection
    cursor.close()
    conn.close() 