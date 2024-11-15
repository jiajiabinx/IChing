from .database import get_db_connection
from psycopg2.extras import RealDictCursor

import json

def insert_user(user_data):
    query = """
    INSERT INTO Users (display_name, birth_date, birth_location, primary_residence, current_location,
                       college, educational_level, parental_income, primary_interest,
                       profession, religion, race)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            user_tuple = cursor.fetchone()
            user = dict(zip([desc[0] for desc in cursor.description], user_tuple))
            conn.commit()
    return user

def update_user(user_data):
    query = """
    UPDATE Users SET 
        display_name = %s,
        birth_date = %s,
        birth_location = %s,
        primary_residence = %s,
        current_location = %s,
        college = %s,
        educational_level = %s,
        parental_income = %s,
        primary_interest = %s,
        profession = %s,
        religion = %s,
        race = %s
    WHERE user_id = %s
    RETURNING *;
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (
                    user_data.get('display_name'), user_data.get('birth_date'), user_data.get('birth_location'),
                    user_data.get('primary_residence'), user_data.get('current_location'), user_data.get('college'),
                    user_data.get('educational_level'), user_data.get('parental_income'), user_data.get('primary_interest'),
                    user_data.get('profession'), user_data.get('religion'), user_data.get('race'), user_data.get('user_id')
                ))
                updated_user = cursor.fetchone()
                conn.commit()
        return updated_user
    except Exception as e:
        print(f"Error updating user: {e}")
        return None

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
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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


def insert_order(amount):
    query = """
    INSERT INTO Orders (amount)
    VALUES (%s)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, ( amount,))
            order = cursor.fetchone()
            conn.commit()
    return order


def check_order_exists(order_id):
    query = """
    SELECT * FROM Orders WHERE order_id = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (order_id,))
            order = cursor.fetchone()
    return order is not None


def create_session_for_order():
    query = """
    INSERT INTO Session (timestamp)
    VALUES (CURRENT_TIMESTAMP)
    RETURNING session_id;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            session_id = cursor.fetchone()
            conn.commit()
    return session_id


def create_completed_payment(user_id, order_id, session_id):
    query = """
    INSERT INTO Completed_Payment (user_id, order_id, session_id)
    VALUES (%s, %s, %s)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (user_id, order_id, session_id))
            completed_payment = cursor.fetchone()
            conn.commit()
    return completed_payment

def record_payment(user_id, order_id):
    if not check_order_exists(order_id):
        raise Exception("Order not found.")
    
    session_id = create_session_for_order()
    
    completed_payment = create_completed_payment(user_id, order_id, session_id)
    
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
    FROM Users, Completed_Payment, Session, Initiated_Transaction, Generated_Story, Display_Story
    WHERE Users.user_id = %s
    AND Completed_Payment.user_id = Users.user_id 
    AND Completed_Payment.session_id = Session.session_id
    AND Initiated_Transaction.session_id = Completed_Payment.session_id
    AND Generated_Story.story_id = Display_Story.story_id
    AND Generated_Story.transaction_id = Initiated_Transaction.transaction_id;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
    