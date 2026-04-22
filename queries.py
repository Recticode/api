from db import get_connection
from psycopg2.extras import RealDictCursor

def get_challenges():
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM challenges;")
        challenges = cursor.fetchall()
        cursor.close()
        return challenges

    finally:
        connection.close()

def get_challenge_repo(name):
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT repo_name FROM challenges WHERE name = %s",
                       (name, )
        )
        challenge = cursor.fetchone()
        cursor.close()
        return challenge
    finally:
        connection.close()

def add_challenge_passed(github_id, challenge_name):
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("INSERT INTO passed (github_user_id, challenge_name) VALUES (%s, %s)",
                       (github_id, challenge_name))
        connection.commit()
        cursor.close()
    finally:
        connection.close()

def has_challenge_been_done(github_id, challenge_name):
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT challenge_name FROM passed WHERE challenge_name = %s AND github_user_id = %s",
                       (challenge_name, github_id))
        challenge = cursor.fetchone()
        cursor.close()
        return challenge
    finally:
        connection.close()

def add_challenge_failed(github_id, challenge_name):
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("INSERT INTO failed (github_user_id, challenge_name) VALUES (%s, %s)",
                       (github_id, challenge_name))
        connection.commit()
        cursor.close()
    finally:
        connection.close()

def has_challenge_been_failed(github_id, challenge_name):
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT challenge_name FROM failed WHERE challenge_name = %s AND github_user_id = %s",
                       (challenge_name, github_id))
        challenge = cursor.fetchone()
        cursor.close()
        return challenge
    finally:
        connection.close()


def get_user_passed_challenges(github_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT challenge_name FROM passed WHERE github_user_id = %s",
                       (github_id, ))
        challenges = cursor.fetchall()
        cursor.close()
        return challenges
    finally:
        connection.close()