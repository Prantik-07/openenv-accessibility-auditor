import tempfile
import subprocess
import json
from bs4 import BeautifulSoup
from models import Observation, Action, Issue

class AccessibilityEnv:
    def __init__(self, task_html: str):
        self.initial_html = task_html
        self.current_html = task_html
        self.baseline_issues = 0
        
    def _run_audit(self, html_content: str) -> list:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode='w') as f:
            f.write(html_content)
            temp_path = f.name
            
        try:
            result = subprocess.run(
                ['pa11y', '--reporter', 'json', f'file://{temp_path}', '--ignore', 'warning'],
                capture_output=True, text=True, timeout=30
            )
            if result.stdout:
                return json.loads(result.stdout)
            return []
        except Exception:
            return []

    def reset(self) -> Observation:
        self.current_html = self.initial_html
        raw_issues = self._run_audit(self.current_html)
        self.baseline_issues = len(raw_issues)
        
        parsed_issues = [Issue(**issue) for issue in raw_issues]
        return Observation(
            current_html=self.current_html,
            audit_issues=parsed_issues,
            total_issues=self.baseline_issues
        )

    def step(self, action: Action) -> tuple[Observation, float, bool, dict]:
        soup = BeautifulSoup(self.current_html, 'html.parser')
        
        try:
            target_element = soup.select_one(action.css_selector)
            if target_element:
                if action.action_type in ['add_attribute', 'update_attribute']:
                    target_element[action.attribute] = action.new_value
                elif action.action_type == 'replace_text':
                    target_element.string = action.new_value
                self.current_html = str(soup)
        except Exception:
            pass 

        new_raw_issues = self._run_audit(self.current_html)
        new_issue_count = len(new_raw_issues)
        
        reward_score = 0.0
        done = False
        
        if new_issue_count == 0:
            reward_score = 1.0
            done = True
        elif new_issue_count < self.baseline_issues:
            reward_score = (self.baseline_issues - new_issue_count) / self.baseline_issues
            
        parsed_issues = [Issue(**issue) for issue in new_raw_issues]
        obs = Observation(
            current_html=self.current_html,
            audit_issues=parsed_issues,
            total_issues=new_issue_count
        )
        
        return obs, round(reward_score, 2), done, {"baseline": self.baseline_issues}