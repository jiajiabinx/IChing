from .database import get_db_connection

import json

def insert_user(user_data):
    query = """
    INSERT INTO Users (birth_date, birth_location, primary_residence, current_location,
                       college, educational_level, parental_income, primary_interest,
                       profession, religion, race)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING user_id;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (
                user_data['birth_date'], user_data['birth_location'], user_data['primary_residence'],
                user_data['current_location'], user_data['college'], user_data['educational_level'],
                user_data['parental_income'], user_data['primary_interest'], user_data['profession'],
                user_data['religion'], user_data['race']
            ))
            user = cursor.fetchone()
            conn.commit()
    return user

def insert_friend(user_id_left, user_id_right):
    query = """
    INSERT INTO Friends (user_id_left, user_id_right)
    VALUES (%s, %s)
    ON CONFLICT DO NOTHING;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (min(user_id_left, user_id_right), max(user_id_left, user_id_right)))
            friend = cursor.fetchone()
            conn.commit()
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

def get_users_by_ids(user_ids):
    user_ids_str = ','.join(map(str, user_ids))
    query = """
    SELECT * FROM Users WHERE user_id IN (%s);
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_ids_str,))
            users = cursor.fetchall()
    return users

def get_random_users( exclude_ids, limit =5):
    query = """
    SELECT * FROM Users 
    WHERE user_id NOT IN (%s) ORDER BY RANDOM() LIMIT %s;
    """
    exclude_ids_str = ','.join(map(str, exclude_ids))
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, ( exclude_ids_str,limit))
            users = cursor.fetchall()
    return users

def get_user_friends(user_id):
    query_get_friends = """
    SELECT CASE
             WHEN user_id_left = %s THEN user_id_right
             ELSE user_id_left
           END AS friend_id
    FROM Friends
    WHERE user_id_left = %s OR user_id_right = %s;
    """
    query_get_friends_detail = """
    SELECT * FROM Users 
    WHERE user_id IN (%s);
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query_get_friends, (user_id, user_id, user_id))
            friends = cursor.fetchall()
            friends_ids = [friend['friend_id'] for friend in friends]
            friends_ids_str = ','.join(friends_ids)
            cursor.execute(query_get_friends_detail, (friends_ids_str,))
            friends_detail = cursor.fetchall()
    return friends_detail


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
    RETURNING order_id;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, amount))
            order_id = cursor.fetchone()[0]
            conn.commit()
    return order_id

def check_user_order(user_id):
    query = """
    SELECT order_id FROM Orders
    WHERE user_id = %s AND NOT EXISTS (
        SELECT 1 FROM Paid_by WHERE Orders.order_id = Paid_by.order_id
    );
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            order = cursor.fetchone()
    return order is not None

def create_session_for_order(order_id):
    query = """
    INSERT INTO Session (order_id, timestamp)
    VALUES (%s, CURRENT_TIMESTAMP)
    RETURNING session_id;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (order_id,))
            session_id = cursor.fetchone()[0]
            conn.commit()
    return session_id

def record_payment(user_id, order_id, session_id):
    query = """
    INSERT INTO Paid_by (user_id, order_id, session_id)
    VALUES (%s, %s, %s);
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, order_id, session_id))
            conn.commit()
            
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
    