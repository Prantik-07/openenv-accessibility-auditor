import os
import json
from openai import OpenAI
from env import AccessibilityEnv
from models import Action

client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.environ.get("HF_TOKEN", os.environ.get("OPENAI_API_KEY", "dummy-key"))
)
model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

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

def run_task(task):
    print(f"[START] Starting task: {task['id']}")
    
    env = AccessibilityEnv(task['html'])
    obs = env.reset()
    final_reward = 0.0
    
    system_prompt = f"""You are an accessibility auditing agent. Fix this issue: {task['description']}.
Respond ONLY with valid JSON matching this schema:
{{"action_type": "add_attribute"|"update_attribute"|"replace_text", "css_selector": "...", "attribute": "...", "new_value": "..."}}"""

    for step_num in range(5):
        print(f"[STEP] Step {step_num + 1}")
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
            
            action_data = json.loads(response.choices[0].message.content)
            obs, reward, done, _ = env.step(Action(**action_data))
            final_reward = reward
            
            if done: break
                
        except Exception:
            break

    print(f"[END] Task {task['id']} completed with final score: {final_reward}")

if __name__ == "__main__":
    for task in TASKS:
        run_task(task)