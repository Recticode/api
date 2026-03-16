from fastapi import FastAPI
from queries import get_challenges, get_challenge_repo

app = FastAPI()

@app.get("/")
async def root():
    return {"Hello": "World"}

@app.get("/list_challenges")
def list_challenges():
    challenges = get_challenges()
    return {"challenges": challenges}

@app.get("/challenge_repo/{name}")
def challenge_repo(name: str):
    challenge = get_challenge_repo(name)
    if challenge is None:
        return {"error": "Challenge name does not exist"}
    else:
        return {"repo_name": "https://github.com/Recticode/" + challenge['repo_name']}