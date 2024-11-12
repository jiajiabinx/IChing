import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from .database import get_db_connection



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
            user_id = cursor.fetchone()[0]
            conn.commit()
    return user_id

def insert_friend(user_id_left, user_id_right):
    query = """
    INSERT INTO Friends (user_id_left, user_id_right)
    VALUES (%s, %s)
    ON CONFLICT DO NOTHING;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (min(user_id_left, user_id_right), max(user_id_left, user_id_right)))
            conn.commit()

def get_user_friends(user_id):
    query = """
    SELECT CASE
             WHEN user_id_left = %s THEN user_id_right
             ELSE user_id_left
           END AS friend_id
    FROM Friends
    WHERE user_id_left = %s OR user_id_right = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (user_id, user_id, user_id))
            friends = cursor.fetchall()
    return [friend['friend_id'] for friend in friends]


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