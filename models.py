from pydantic import BaseModel, Field
from typing import List, Optional

class Issue(BaseModel):
    code: str = Field(description="The WCAG error code")
    message: str = Field(description="Human readable description of the error")
    selector: str = Field(description="The CSS selector of the failing element")
    context: str = Field(description="The HTML snippet of the failing element")

class Observation(BaseModel):
    current_html: str = Field(description="The full HTML source code of the current page state")
    audit_issues: List[Issue] = Field(description="List of currently active accessibility violations")
    total_issues: int = Field(description="The total count of active violations")

class Action(BaseModel):
    action_type: str = Field(description="Must be one of: 'add_attribute', 'update_attribute', 'replace_text'")
    css_selector: str = Field(description="The CSS selector of the element to modify")
    attribute: Optional[str] = Field(None, description="The HTML attribute to modify")
    new_value: str = Field(description="The new string value to inject")

class Reward(BaseModel):
    score: float = Field(description="Float between 0.0 and 1.0 representing improvement")
    reasoning: str = Field(description="Explanation of the reward calculation")