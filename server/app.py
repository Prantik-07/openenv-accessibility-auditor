import sys
import os
# This ensures it can still read your env.py and models.py files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI
from env import AccessibilityEnv
from models import Action

app = FastAPI()

default_html = """<div id="hero"><img src="/assets/hero.jpg" alt="hero"><h1>Welcome</h1></div>"""
server_env = AccessibilityEnv(default_html)

@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    obs = server_env.reset()
    return obs

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = server_env.step(action)
    return {
        "observation": obs,
        "reward": float(reward),
        "done": bool(done),
        "info": info
    }

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()