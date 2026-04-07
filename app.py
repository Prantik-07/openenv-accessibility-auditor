from fastapi import FastAPI
from env import AccessibilityEnv
from models import Action

app = FastAPI()

# Initialize a default environment to keep the web server alive
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

@app.get("/state")
def state():
    return {"status": "running"}