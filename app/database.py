from contextlib import contextmanager
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(os.getenv('DB_URI'))

@contextmanager
def get_db_connection():
    conn = engine.connect()
    try:
        yield conn.connection
    except Exception as e:
        conn.rollback()
        raise "Connection Error"
    finally:
        conn.close()
