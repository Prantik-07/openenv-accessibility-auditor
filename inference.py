import os
import json
from openai import OpenAI
from env import AccessibilityEnv
from models import Action

# 1. INITIALIZE OPENAI CLIENT
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.environ.get("HF_TOKEN")

# Give OpenAI a dummy key only if HF_TOKEN is empty so it doesn't crash on startup
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN if HF_TOKEN else "dummy-key"
)

# 2. DEFINE THE TASKS
TASKS = [
    {
        "id": "task_1_easy_alt_text",
        "description": "Fix the missing alt attribute on the hero image.",
        "html": """<div id="hero"><img id="hero-image" src="/assets/hero.jpg"><h1>Welcome</h1></div>"""
    },
    {
        "id": "task_2_medium_contrast",
        "description": "Update the inline style of the button to pass WCAG AA contrast ratios.",
        "html": """<div class="alert"><p>Warning</p><button id="warning-btn" style="color: #cccccc; background-color: #ffffff;">Renew Now</button></div>"""
    },
    {
        "id": "task_3_hard_aria_roles",
        "description": "Add proper ARIA roles to make this custom modal accessible.",
        "html": """<div id="custom-modal" class="hidden"><div id="modal-content"><h2>Info</h2><button id="close-modal">Close</button></div></div>"""
    },
    {
        "id": "task_4_medium_form_labels",
        "description": "Fix the disconnected form label.",
        "html": """<form class="signup-form"><label>Email Address</label><input type="email" id="email-input" name="email"><button type="submit">Submit</button></form>"""
    },
    {
        "id": "task_5_hard_interactive_tabindex",
        "description": "This custom dropdown cannot be reached using the keyboard. Fix the tabindex.",
        "html": """<div class="custom-select"><div id="dropdown-trigger" class="trigger" onclick="toggleMenu()">Select Option</div><ul id="dropdown-menu" class="hidden"><li>Option 1</li></ul></div>"""
    }
]

# 3. AGENT EXECUTION LOOP
def run_task(task):
    env_name = "accessibility-pipeline-auditor"
    
    # STRICT FORMAT: [START] task=<task_name> env=<benchmark> model=<model_name>
    print(f"[START] task={task['id']} env={env_name} model={model_name}")
    
    env = AccessibilityEnv(task['html'])
    obs = env.reset()
    
    final_reward = 0.0
    reward_history = []
    success = False
    actual_steps = 0
    
    system_prompt = f"""You are an accessibility auditing agent. Fix this issue: {task['description']}.
Respond ONLY with valid JSON matching this schema:
{{"action_type": "add_attribute"|"update_attribute"|"replace_text", "css_selector": "...", "attribute": "...", "new_value": "..."}}"""

    for step_num in range(5):
        actual_steps += 1
        action_str = "null"
        step_reward = 0.0
        done = False
        error_msg = "null"
        
        user_prompt = f"HTML:\n{obs.current_html}\n\nIssues:\n{json.dumps([i.model_dump() for i in obs.audit_issues])}\n\nNext action?"
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            raw_action = response.choices[0].message.content
            action_data = json.loads(raw_action)
            action_str = json.dumps(action_data).replace(" ", "") # Minify JSON string to avoid breaking logs
            
            obs, reward, done, _ = env.step(Action(**action_data))
            step_reward = float(reward)
            final_reward = step_reward
            
        except Exception as e:
            error_msg = str(e).replace('\n', ' ') # Ensure no new lines break the log
            done = True

        reward_history.append(f"{step_reward:.2f}")
        success = done and final_reward == 1.0

        # STRICT FORMAT: [STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
        print(f"[STEP] step={actual_steps} action={action_str} reward={step_reward:.2f} done={str(done).lower()} error={error_msg}")

        if done:
            break

    # STRICT FORMAT: [END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
    rewards_str = ",".join(reward_history)
    print(f"[END] success={str(success).lower()} steps={actual_steps} score={final_reward:.2f} rewards={rewards_str}")

# 4. RUN ALL TASKS
if __name__ == "__main__":
    for task in TASKS:
        run_task(task)