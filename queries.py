from db import pool
from psycopg2.extras import RealDictCursor

def get_challenges():
    connection = pool.getconn()  # grab a connection from the pool

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM challenges;")
        challenges = cursor.fetchall()
        cursor.close()
        return challenges

    finally:
        pool.putconn(connection)  # return connection to the pool

def get_challenge_repo(name):
    connection = pool.getconn()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT repo_name FROM challenges WHERE name = %s",
                       (name, )
        )
        challenge = cursor.fetchone()
        cursor.close()
        return challenge
    finally:
        pool.putconn(connection)
