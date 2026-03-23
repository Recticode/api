from fastapi import FastAPI, UploadFile, File
from queries import get_challenges, get_challenge_repo, add_challenge_passed
from ratelimit import is_rate_limited, is_submit_rate_limited, fetch_user_id_from_token
from fastapi import HTTPException
import os
import requests

app = FastAPI()

@app.get("/")
async def root():
    return {"Hello": "There"}

@app.get("/list_challenges")
def list_challenges(token: str | None = None):
    if token is None or is_rate_limited(token):
        raise HTTPException(status_code=429, detail="rate limited")
    else:
        challenges = get_challenges()
        return {"challenges": challenges}

@app.get("/challenge_repo/{name}")
def challenge_repo(name: str, token: str | None = None):
    if is_rate_limited(token):
        raise HTTPException(status_code=429, detail="rate limited")
    else:
        challenge = get_challenge_repo(name)
        if challenge is None:
            return {"error": "Challenge name does not exist"}
        else:
            return {"repo_name": "https://github.com/Recticode/" + challenge['repo_name']}

@app.post("/submit/{challenge_name}")
def submit(challenge_name: str, file: UploadFile = File(...), token: str | None = None):
    if is_submit_rate_limited(token):
        raise HTTPException(status_code=429, detail="rate limited")
    else:
        challenge = get_challenge_repo(challenge_name)
        if challenge is None:
            raise HTTPException(status_code=400, detail="challenge name does not exist")

        with open('zipfile.zip', 'rb') as f:
            headers = {
                "x-internal-key": os.getenv("INTERNAL_KEY")
            }
            r = requests.post(os.getenv("SUBMIT_URL"), files={'file': f},
                              headers=headers)
            print(r.json())
            correct = r.json()['correct']
            total = r.json()['total']
            if correct == total:
                github_user_id = fetch_user_id_from_token(token)
                add_challenge_passed(github_user_id, challenge_name)
                return {"passed": True, correct: correct, total: total}
            else:
                return {"passed": False, correct: correct, total: total}