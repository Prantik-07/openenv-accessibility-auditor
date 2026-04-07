---
title: Openenv Accessibility Auditor
emoji: ♿
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
# Accessibility Pipeline Auditor (OpenEnv)

## Motivation and Real-World Utility
Web accessibility (WCAG compliance) is a critical legal and ethical requirement, yet it is often caught late in the development cycle. This environment simulates a real-world CI/CD pipeline QA agent. The agent is handed raw, inaccessible HTML DOM strings and must programmatically patch the HTML to pass a strict, headless `pa11y` accessibility audit. This moves beyond standard text-generation and tests an agent's ability to understand DOM structures, CSS properties, and ARIA state management.

## Environment Design

### Observation Space
At each step, the agent observes the current state of the DOM and a programmatic audit report:
* `current_html` (str): The raw HTML string.
* `audit_issues` (List[Issue]): A list of active WCAG violations, including the error code, human-readable message, and the specific CSS selector of the failing element.
* `total_issues` (int): Count of remaining issues.

### Action Space
The agent patches the DOM using a structured JSON action:
* `action_type` (str): 'add_attribute', 'update_attribute', or 'replace_text'.
* `css_selector` (str): Targets the element to fix.
* `attribute` (str, optional): The HTML attribute to modify (e.g., 'aria-label', 'style').
* `new_value` (str): The injected fix.

### Reward Function
The environment uses **Dense Reward Shaping**. 
Instead of a sparse binary pass/fail, the agent receives partial credit for reducing the total number of accessibility violations compared to the baseline. 
`Reward = (Baseline Issues - Current Issues) / Baseline Issues`
A perfect score of `1.0` is awarded when 0 issues remain.

## Tasks & Difficulty Progression
1. **Easy**: Inject missing `alt` text into image tags.
2. **Medium**: Correct inline CSS color hex codes to pass WCAG AA contrast ratios.
3. **Hard**: Inject complex ARIA roles and tabindex states into a custom modal component.
4. **Medium**: Re-associate disconnected form `<label>` tags with their corresponding inputs.
5. **Hard**: Restore keyboard navigability to a non-semantic `<div>` functioning as a dropdown.

## Setup Instructions
```bash
docker build -t a11y-auditor .
docker run -e OPENAI_API_KEY="your-key" a11y-auditor

