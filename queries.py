from db import get_connection
from psycopg2.extras import RealDictCursor
from ratelimit import fetch_user_data_from_token

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

def does_user_exist(github_user_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id FROM users WHERE github_user_id = %s",
                       (github_user_id,))
        user_id = cursor.fetchone()
        cursor.close()
        return not (user_id is None)
    finally:
        connection.close()

def create_user(access_token):
    user_data = fetch_user_data_from_token(access_token)
    if user_data is None:
        return False

    github_user_id = user_data.get("id")
    user_exists = does_user_exist(github_user_id)

    if user_exists:
        return True

    github_username = user_data.get("login")

    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("INSERT INTO users (github_user_id, github_username) VALUES (%s, %s)",
                       (github_user_id, github_username))
        connection.commit()
        cursor.close()
    finally:
        connection.close()

    return True
