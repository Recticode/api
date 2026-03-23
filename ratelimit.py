import redis
import os
from dotenv import load_dotenv
import requests

load_dotenv()

r = redis.Redis.from_url(
    os.environ['REDIS_URI'],
    decode_responses=True
)

def fetch_user_id_from_token(access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.get("https://api.github.com/user", headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    user_json = response.json()
    return user_json.get("id")

def is_rate_limited(access_token: str, limit=10, window=60):
    user_id = r.get(f"token:{access_token}")

    if user_id is None:
        user_id = fetch_user_id_from_token(access_token=access_token)
        if user_id:
            r.setex(f"token:{access_token}", 3600, user_id)  # cache 1 hour
        else:
            return True

    key = f"rate:{user_id}"

    current = r.incr(key)
    if current == 1:
        r.expire(key, window)

    return current > limit

def is_submit_rate_limited(access_token: str, limit=3, window=300):
    user_id = r.get(f"token:{access_token}")

    if user_id is None:
        user_id = fetch_user_id_from_token(access_token=access_token)
        if user_id:
            r.setex(f"token:{access_token}", 3600, user_id)
        else:
            return True

    key = f"submit_rate:{user_id}"
    current = r.incr(key)
    if current == 1:
        r.expire(key, window)

    return current > limit