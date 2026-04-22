from fastapi import FastAPI, UploadFile, File
from queries import get_challenges, get_challenge_repo, add_challenge_passed, has_challenge_been_done, get_user_passed_challenges, has_challenge_been_failed, add_challenge_failed, create_user
from ratelimit import is_rate_limited, is_submit_rate_limited, fetch_user_data_from_token
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

@app.get("/passed_challenges")
def passed_challenges(token: str | None = None):
    if is_rate_limited(token):
        raise HTTPException(status_code=429, detail="rate limited")
    else:
        github_user_id = fetch_user_data_from_token(token).get("id")
        challenges = get_user_passed_challenges(github_user_id)
        return {"challenges": challenges}


@app.post("/submit/{challenge_name}")
def submit(challenge_name: str, file: UploadFile = File(...), token: str | None = None):
    if is_submit_rate_limited(token):
        raise HTTPException(status_code=429, detail="rate limited")
    else:
        challenge = get_challenge_repo(challenge_name)
        if challenge is None:
            raise HTTPException(status_code=400, detail="challenge name does not exist")

        headers = {
            "x-internal-key": os.getenv("INTERNAL_KEY")
        }

        r = requests.post(
            os.getenv("SUBMIT_URL") + "/" + challenge_name,
            files={'file': (file.filename, file.file, file.content_type)},
            headers=headers
        )
        print("STATUS:", r.status_code)
        print("BODY:", r.text)

        if r.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"submit server error: {r.status_code}"
            )

        try:
            resp_json = r.json()
        except Exception:
            raise HTTPException(
                status_code=500,
                detail=f"submit returned non-json: {r.text}"
            )

        correct = resp_json.get('correct')
        total = resp_json.get('total')
        if correct is None or total is None:
            raise HTTPException(status_code=500, detail="submit server returned invalid response")
        github_user_id = fetch_user_data_from_token(token).get("id")
        if correct == total:
            challenge_done = has_challenge_been_done(github_user_id, challenge_name)
            if challenge_done is None:
                add_challenge_passed(github_user_id, challenge_name)
            return {"passed": True, "correct": correct, "total": total}
        else:
            challenge_failed = has_challenge_been_failed(github_user_id, challenge_name)
            if challenge_failed is None:
                add_challenge_failed(github_user_id, challenge_name)
            return {"passed": False, "correct": correct, "total": total}

@app.get("/login")
def login(token: str | None = None):
    if is_rate_limited(token):
        raise HTTPException(status_code=429, detail="rate limited")
    else:
        result = create_user(access_token=token)
        return {"result": result}