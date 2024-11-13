from .database import get_db_connection

import json

def insert_user(user_data):
    query = """
    INSERT INTO Users (display_name, birth_date, birth_location, primary_residence, current_location,
                       college, educational_level, parental_income, primary_interest,
                       profession, religion, race)
    VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (
                user_data['display_name'], user_data['birth_date'], user_data['birth_location'], 
                user_data['primary_residence'], user_data['current_location'], user_data['college'],
                user_data['educational_level'], user_data['parental_income'], user_data['primary_interest'],
                user_data['profession'], user_data['religion'], user_data['race']
            ))
            user = cursor.fetchone()
            conn.commit()
    return user

def insert_friend(user_id_left, user_id_right):
    query = """
    INSERT INTO Friends (user_id_left, user_id_right)
    VALUES (%s, %s)
    ON CONFLICT DO NOTHING
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (min(user_id_left, user_id_right), max(user_id_left, user_id_right)))
            friend = cursor.fetchone()
            conn.commit()
    
    if not friend:
        raise Exception("Friend relationship already exists or invalid user IDs.")
    
    return friend

def get_user_by_id(user_id):
    query = """
    SELECT * FROM Users WHERE user_id = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
    return user

def get_random_users(exclude_ids, limit =5):
    exclude_ids_str = ','.join(map(str, exclude_ids))
    query = f"""
    SELECT * FROM Users 
    WHERE user_id NOT IN ({exclude_ids_str})
    ORDER BY RANDOM() LIMIT %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (limit,))
            random_users = cursor.fetchall()
    return random_users

def get_user_friends(user_id):
    query = """
    SELECT Users.* FROM Users
    INNER JOIN Friends ON (Users.user_id = Friends.user_id_left AND Friends.user_id_right = %s)
                        OR (Users.user_id = Friends.user_id_right AND Friends.user_id_left = %s);
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, user_id))
            friends = cursor.fetchall()
    
    return friends

def delete_user(user_id):
    query = """
    DELETE FROM Users WHERE user_id = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            conn.commit()


def insert_order(user_id, amount):
    query = """
    INSERT INTO Orders (user_id, amount)
    VALUES (%s, %s)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, amount))
            order = cursor.fetchone()
            conn.commit()
    return order


def check_order_exists(user_id, order_id):
    query = """
    SELECT * FROM Orders WHERE user_id = %s AND order_id = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, order_id))
            order = cursor.fetchone()
    return order is not None


def create_session_for_order(order_id):
    query = """
    INSERT INTO Session (order_id, timestamp)
    VALUES (%s, CURRENT_TIMESTAMP)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (order_id,))
            session = cursor.fetchone()
            conn.commit()
    return session


def create_completed_payment(user_id, order_id, session_id):
    query = """
    INSERT INTO CompletedPayment (user_id, order_id, session_id)
    VALUES (%s, %s, %s)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, order_id, session_id))
            completed_payment = cursor.fetchone()
            conn.commit()
    return completed_payment

def record_payment(user_id, order_id):
    if not check_order_exists(user_id, order_id):
        raise Exception("Order not found or does not belong to the specified user.")
    
    session = create_session_for_order(order_id)
    
    completed_payment = create_completed_payment(user_id, order_id, session[0])
    
    return completed_payment
        
            
def yun_suan(user_data, count = 3):
    query = """
    SELECT *
        FROM wiki_reference
        ORDER BY RANDOM()
        LIMIT %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (count,))
            references = cursor.fetchall()
    return references

def get_user_historical_sessions(user_id):
    query = """
    SELECT * 
    FROM Users, CompletedPayment, InitiatedTransaction, DisplayStory
    WHERE Users.user_id = %s 
    AND CompletedPayment.user_id = Users.user_id 
    AND InitiatedTransaction.session_id = CompletedPayment.session_id
    AND DisplayStory.transaction_id = InitiatedTransaction.transaction_id
    
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            history = cursor.fetchall()
    return history

    
def record_APICall(user, references, transaction_data):
    query = """
    INSERT INTO APICall (user_id, references, transaction_data)
    VALUES (%s, %s, %s);
    """
    references_str = json.dumps(references)
    user_str = json.dumps(user)
    prompt = 'Create a story based on the following historical figures: ' + references_str + ' and the biography of the following person: ' + user_str
    