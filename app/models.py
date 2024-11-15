from .database import get_db_connection
from psycopg2.extras import RealDictCursor
import uuid
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

def update_user(user_data):
    query = """
    UPDATE Users SET 
    """ 
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_data['user_id'], user_data['display_name'], user_data['birth_date'], user_data['birth_location'], user_data['primary_residence'], user_data['current_location'], user_data['college'], user_data['educational_level'], user_data['parental_income'], user_data['primary_interest'], user_data['profession'], user_data['religion'], user_data['race']))
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


def check_order_exists(user_id, order_id):
    query = """
    SELECT * FROM Orders WHERE user_id = %s AND order_id = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id, order_id))
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

    
def record_APICall(transaction_id, session_id, prompt):
    record_transaction_query = """
    INSERT INTO Initiated_Transaction (transaction_id, session_id)
    VALUES (%s, %s);
    """
    record_API_call_query = """
    INSERT INTO API_Call (transaction_id, prompt)
    VALUES (%s, %s);
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(record_transaction_query, (transaction_id, session_id))
            cursor.execute(record_API_call_query, (transaction_id, prompt))
            conn.commit()
    return transaction_id

def record_sbert_call(transaction_id, session_id, corpus):
    
    record_transaction_query = """
    INSERT INTO Initiated_Transaction (transaction_id, session_id)
    VALUES (%s, %s);
    """
    record_sbert_call_query = """
    INSERT INTO SBERT_Call (transaction_id, corpus)
    VALUES (%s, %s);
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(record_transaction_query, (transaction_id, session_id))
            cursor.execute(record_sbert_call_query, (transaction_id, corpus))
            conn.commit()
    return transaction_id

def insert_temp_story(transaction_id, generated_story_text):
    generated_story_query = """
    INSERT INTO Generated_Story (transaction_id, generated_story_text)
    VALUES (%s, %s)
    RETURNING *;
    """
    temp_story_query = """
    INSERT INTO Temp_Story (story_id)
    VALUES (%s)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(generated_story_query, (transaction_id, generated_story_text))
            generated_story = cursor.fetchone()
            cursor.execute(temp_story_query, (generated_story['story_id'],))
            temp_story = cursor.fetchone()
            conn.commit()
    return temp_story

def insert_display_story(transaction_id, references, reference_summary, generated_story_text):
    generated_story_query = """
    INSERT INTO Generated_Story (transaction_id, generated_story_text)
    VALUES (%s, %s)
    RETURNING *;
    """ 
    display_story_query = """
    INSERT INTO Display_Story (story_id, "references", reference_summary)
    VALUES (%s, %s, %s);
    """
    get_story_query = """
    SELECT * FROM Generated_Story, Display_Story
    WHERE Display_Story.story_id = %s
    AND Generated_Story.story_id = Display_Story.story_id;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(generated_story_query, (transaction_id, generated_story_text,))
            generated_story = cursor.fetchone()
            cursor.execute(display_story_query, (generated_story['story_id'], references, reference_summary ))
            cursor.execute(get_story_query, (generated_story['story_id'],))
            display_story = cursor.fetchone()
            conn.commit()
    return display_story

def get_display_story(story_id):
    query = """
    SELECT * 
    FROM Display_Story, Generated_Story
    WHERE Display_Story.story_id = Generated_Story.story_id
    AND Display_Story.story_id = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (story_id,))
            display_story = cursor.fetchone()
    return display_story


def record_identified_relationships(story_id, wiki_reference_ids):
    query = """
    INSERT INTO Identified (story_id, wiki_page_id)
    VALUES (%s, %s)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            for r in wiki_reference_ids:
                cursor.execute(query, (story_id, r))
            identified_relationships = cursor.fetchall()
            conn.commit()
    return identified_relationships
  
def record_referred_relationship(story_id,transaction_id):
    query = """
    INSERT INTO Referred (story_id, transaction_id)
    VALUES (%s, %s)
    RETURNING *;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (story_id, transaction_id))
            referred_relationships = cursor.fetchone()
            conn.commit()
    return referred_relationships
        
def check_payment(user_id, session_id, order_id):
    query = """
    SELECT * FROM Completed_Payment 
    WHERE user_id = %s 
    AND session_id = %s 
    AND order_id = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (user_id, session_id, order_id))
            payment = cursor.fetchone()
    return payment is not None

def get_identified_references_by_display_story_id(display_story_id):
    query = """
    WITH SessionInfo AS (
        SELECT Initiated_Transaction.session_id
        FROM Generated_Story, API_Call, Initiated_Transaction
        WHERE Generated_Story.story_id = %s
        AND Generated_Story.transaction_id = API_Call.transaction_id
        AND API_Call.transaction_id = Initiated_Transaction.transaction_id
    )
    SELECT DISTINCT Wiki_Reference.*
    FROM  Initiated_Transaction, Referred, Identified, Wiki_Reference
    WHERE Initiated_Transaction.session_id = (SELECT session_id FROM SessionInfo)
    AND Referred.transaction_id = Initiated_Transaction.transaction_id
    AND Identified.story_id = Referred.story_id
    AND Wiki_Reference.wiki_page_id = Identified.wiki_page_id;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (display_story_id,))
            references = cursor.fetchall()
    return references

def get_identified_references_by_session_id(session_id):
    query ="""
    SELECT DISTINCT Wiki_Reference.*
    FROM  Initiated_Transaction, Referred, Identified, Wiki_Reference
    WHERE Initiated_Transaction.session_id = %s
    AND Referred.transaction_id = Initiated_Transaction.transaction_id
    AND Identified.story_id = Referred.story_id
    AND Wiki_Reference.wiki_page_id = Identified.wiki_page_id;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (session_id,))
            identified_references = cursor.fetchall()
    return identified_references

def get_temp_story(story_id):
    query = """
    SELECT 
        ts.story_id,
        gs.transaction_id,
        gs.generated_story_text
    FROM Temp_Story ts, Generated_Story gs
    WHERE ts.story_id = gs.story_id
    AND ts.story_id = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (story_id,))
            temp_story = cursor.fetchone()
    return temp_story

def get_random_wiki_references(n):
    query = """
    SELECT * FROM Wiki_Reference ORDER BY RANDOM() LIMIT %s;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (n,))
            wiki_references = cursor.fetchall()
    return wiki_references