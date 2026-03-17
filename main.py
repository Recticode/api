from fastapi import FastAPI
from queries import get_challenges, get_challenge_repo
from ratelimit import is_rate_limited
from fastapi import HTTPException
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