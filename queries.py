from db import get_connection
from psycopg2.extras import RealDictCursor
from ratelimit import fetch_user_data_from_token

def get_user_id_from_github(github_user_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id FROM users WHERE github_user_id = %s",
            (github_user_id,)
        )
        result = cursor.fetchone()
        cursor.close()

        return result["id"] if result else None
    finally:
        connection.close()

def get_challenge_id_from_name(challenge_name):
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id FROM challenges WHERE name = %s",
            (challenge_name,)
        )
        result = cursor.fetchone()
        cursor.close()

        return result["id"] if result else None
    finally:
        connection.close()

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
                       (name, ))
        challenge = cursor.fetchone()
        cursor.close()
        return challenge
    finally:
        connection.close()

def add_challenge_attempt(github_id, challenge_name, status):
    # status must be "success" or score in the format "/"
    user_id = get_user_id_from_github(github_id)
    challenge_id = get_challenge_id_from_name(challenge_name)
    connection = get_connection()

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("INSERT INTO challenge_attempts (user_id, challenge_id, status) VALUES (%s, %s, %s)",
                       (user_id, challenge_id, status))
        connection.commit()
        cursor.close()
    finally:
        connection.close()

def has_challenge_been_done(github_id, challenge_name):
    connection = get_connection()
    user_id = get_user_id_from_github(github_id)
    challenge_id = get_challenge_id_from_name(challenge_name)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT challenge_id FROM challenge_attempts WHERE challenge_id = %s AND user_id = %s AND status = %s",
                       (challenge_id, user_id, "success"))
        challenge = cursor.fetchone()
        cursor.close()
        return challenge
    finally:
        connection.close()

def get_user_passed_challenges(github_id):
    connection = get_connection()
    user_id = get_user_id_from_github(github_id)

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                       SELECT c.name
                       FROM challenge_attempts a
                       JOIN challenges c ON a.challenge_id = c.id
                       WHERE a.user_id = %s
                         AND a.status = %s
                       """, (user_id, "success"))
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
