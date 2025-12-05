# Example Integrations - Real Use Cases

This document shows **actual working examples** of how to integrate the backcasting engine into different systems.

## 1. MCP Integration with Claude Code (Primary Use Case)

### Setup Instructions

1. **Find your Claude Code MCP config file:**
   ```bash
   ~/.config/claude-code/mcp_settings.json
   ```
   (Create it if it doesn't exist)

2. **Add this configuration:**
   ```json
   {
     "mcpServers": {
       "backcast": {
         "command": "python3",
         "args": [
           "/home/panda/Documents/PythonScripts/OutcomeBackcasting/mcp_server.py"
         ],
         "env": {}
       }
     }
   }
   ```

3. **Restart Claude Code**

### Example Conversations

**Example 1: Create a Plan**
```
You: "Create a backcasting plan for launching my YouTube channel
      focused on AI tutorials. Timeline is 6 months, goal is 10,000
      subscribers."

Claude: *[Calls backcast_create_plan tool]*

I've created a backcasting plan "Launch AI Tutorial YouTube Channel"
with 5 major phases working backwards from 10,000 subscribers:

✓ Generated 21 steps including:
  - Phase 5: Hit 10K subscribers milestone
  - Phase 4: Optimize and scale content
  - Phase 3: Build audience engagement
  - Phase 2: Create first batch of videos
  - Phase 1: Channel setup and planning

Would you like to see your next actionable steps?
```

**Example 2: Check Progress**
```
You: "What should I work on next for my YouTube channel plan?"

Claude: *[Calls backcast_get_next_actions tool]*

Here are your next actionable steps (dependencies met):

🔴 CRITICAL - [Step 3] Record first 5 tutorial videos
   - Duration: 2 weeks
   - Success: 5 videos recorded and edited

🟠 HIGH - [Step 5] Set up thumbnail templates
   - Duration: 3 days
   - Success: Template system ready in Canva

🟡 MEDIUM - [Step 7] Write scripts for next 10 videos
   - Duration: 1 week

Which one would you like to start with?
```

**Example 3: Update Status**
```
You: "I just finished recording the 5 videos. Mark step 3 as complete."

Claude: *[Calls backcast_update_step_status tool]*

✓ Updated Step 3 to completed!

Your plan is now 18% complete (4/21 steps done).

New next actions available:
- [Step 6] Upload first video to YouTube
- [Step 8] Create channel trailer

Great progress! Would you like me to analyze your critical path?
```

**Example 4: Get Analysis**
```
You: "Analyze my YouTube plan and tell me if there are any risks"

Claude: *[Calls backcast_analyze_plan tool]*

📊 PLAN ANALYSIS:

Progress: 32% complete (7/21 steps)
On Track: Yes (ahead by 2 weeks)

⚠️ HIGH-PRIORITY RISKS:
1. Video quality inconsistent (Step 12)
   - Probability: Medium, Impact: High
   - Mitigation: Set up quality checklist

2. Audience growth slower than expected (Step 18)
   - Probability: Medium, Impact: High
   - Mitigation: Multiple promotion channels

💡 OPTIMIZATION SUGGESTIONS:
- Steps 9 and 10 can be parallelized (save 1 week)
- Step 15 is a bottleneck (3 other steps depend on it)
- Consider starting Step 15 earlier

Would you like me to help adjust the plan?
```

---

## 2. Python Script Integration

### Example 1: Daily Progress Checker

Create `check_progress.py`:

```python
#!/usr/bin/env python3
"""
Daily script to check progress on all active plans
Run via cron: 0 9 * * * /path/to/check_progress.py
"""

import sys
sys.path.append('/home/panda/Documents/PythonScripts/OutcomeBackcasting')

from backcast_engine import BackcastEngine

engine = BackcastEngine()

# Load all plans
for plan_file in engine.list_plans():
    plan = engine.load_plan(plan_file)
    progress = engine.calculate_progress(plan)

    if progress['blocked'] > 0:
        print(f"⚠️  {plan.outcome.title}: {progress['blocked']} BLOCKED STEPS!")

    if progress['in_progress'] == 0 and progress['completed'] < progress['total']:
        print(f"⏸️  {plan.outcome.title}: No active work!")

    # Get next actions
    next_actions = engine.get_next_actions(plan)
    if next_actions:
        print(f"📋 {plan.outcome.title}: {len(next_actions)} actions ready")
        for action in next_actions[:3]:
            print(f"   - {action.title}")
```

### Example 2: Automated Status Updates from Git

Update plan when you commit code:

```python
#!/usr/bin/env python3
"""
Git post-commit hook to auto-update backcasting plans
.git/hooks/post-commit
"""

import subprocess
import re
import sys
sys.path.append('/home/panda/Documents/PythonScripts/OutcomeBackcasting')

from backcast_engine import BackcastEngine, StepStatus

# Get commit message
commit_msg = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode()

# Check for backcast tags: [backcast:planname:stepid:status]
match = re.search(r'\[backcast:([^:]+):(\d+):(\w+)\]', commit_msg)

if match:
    plan_name, step_id, status = match.groups()

    engine = BackcastEngine()
    plan = engine.load_plan(f"{plan_name}.json")
    plan = engine.update_step(
        plan,
        int(step_id),
        status=StepStatus(status)
    )
    engine.save_plan(plan, f"{plan_name}.json")

    print(f"✓ Updated {plan_name} step {step_id} to {status}")
```

Usage:
```bash
git commit -m "Implement authentication [backcast:saas_launch:5:completed]"
# Auto-updates step 5 in saas_launch.json to completed
```

---

## 3. Webhook Integration

### Example: Slack Notifications

Create `webhook_handler.py`:

```python
#!/usr/bin/env python3
"""
Wrapper around backcast engine that sends Slack notifications
"""

import sys
import requests
sys.path.append('/home/panda/Documents/PythonScripts/OutcomeBackcasting')

from backcast_engine import BackcastEngine, StepStatus

SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

class BackcastWithNotifications:
    def __init__(self):
        self.engine = BackcastEngine()

    def update_step(self, plan, step_id, status):
        """Update step and notify Slack"""
        step = next(s for s in plan.steps if s.id == step_id)
        old_status = step.status

        # Update
        plan = self.engine.update_step(plan, step_id, status=status)

        # Notify
        if status == StepStatus.COMPLETED:
            progress = self.engine.calculate_progress(plan)
            message = {
                "text": f"✅ *{step.title}* completed!\n"
                        f"Plan: {plan.outcome.title}\n"
                        f"Progress: {progress['percent']}%"
            }
            requests.post(SLACK_WEBHOOK, json=message)

        return plan

# Usage
bc = BackcastWithNotifications()
plan = bc.engine.load_plan("my_plan.json")
plan = bc.update_step(plan, step_id=5, status=StepStatus.COMPLETED)
bc.engine.save_plan(plan, "my_plan.json")
```

---

## 4. Integration with Existing Projects

### Example: ComfyUI Workflow Planning

Since you have ComfyUI installed, use backcasting to plan a ComfyUI project:

```python
#!/usr/bin/env python3
"""
Plan a ComfyUI project using backcasting
"""

import sys
sys.path.append('/home/panda/Documents/PythonScripts/OutcomeBackcasting')

from backcast_engine import (
    BackcastEngine, Outcome, Step,
    StepType, Priority, StepStatus
)

engine = BackcastEngine()

# Create outcome
outcome = Outcome(
    title="Build Custom ComfyUI Workflow for Product Photography",
    description="Create automated workflow that takes product images and "
                "generates 10 marketing variations with different backgrounds",
    success_criteria=[
        "Workflow processes images in < 30 seconds",
        "Generates 10 variations with consistent quality",
        "Background removal accuracy > 95%",
        "Easy to use for non-technical users"
    ],
    constraints=[
        "Must run on local GPU",
        "2 week timeline",
        "Use existing ComfyUI nodes when possible"
    ],
    timeline="2 weeks"
)

plan = engine.create_plan(outcome)

# Add specific steps
steps_data = [
    {
        "title": "Research available ComfyUI nodes",
        "description": "Identify nodes for background removal, image generation, batching",
        "type": StepType.ACTION,
        "priority": Priority.HIGH,
        "duration": "1 day"
    },
    {
        "title": "Create base workflow",
        "description": "Build workflow that processes single image",
        "type": StepType.ACTION,
        "priority": Priority.CRITICAL,
        "duration": "2 days"
    },
    {
        "title": "Add batch processing",
        "description": "Extend to handle multiple images automatically",
        "type": StepType.ACTION,
        "priority": Priority.HIGH,
        "duration": "2 days"
    },
    {
        "title": "Create UI wrapper",
        "description": "Simple GUI for non-technical users",
        "type": StepType.ACTION,
        "priority": Priority.MEDIUM,
        "duration": "3 days"
    },
    {
        "title": "Test with real products",
        "description": "Run on 100 product images, validate quality",
        "type": StepType.MILESTONE,
        "priority": Priority.CRITICAL,
        "duration": "1 day"
    }
]

# Add steps with dependencies
for i, step_data in enumerate(steps_data, 1):
    step = Step(
        id=i,
        title=step_data["title"],
        description=step_data["description"],
        type=step_data["type"],
        priority=step_data["priority"],
        status=StepStatus.NOT_STARTED,
        estimated_duration=step_data["duration"],
        resources_needed=[],
        dependencies=[i-1] if i > 1 else [],
        success_criteria=[],
        risks=[]
    )
    plan = engine.add_step(plan, step)

engine.save_plan(plan, "comfyui_product_workflow.json")
print("✓ ComfyUI project plan created!")
```

---

## 5. Voice Assistant Integration

### Extend Your Voice Chat with Backcasting

Add to `/home/panda/voice_chat.py`:

```python
# Add import at top
import sys
sys.path.append('/home/panda/Documents/PythonScripts/OutcomeBackcasting')
from backcast_engine import BackcastEngine, StepStatus

# In main loop, add command detection
engine = BackcastEngine()
active_plan = None

# ... existing voice chat code ...

if "load plan" in user_speech.lower():
    # Extract plan name
    plan_name = extract_plan_name(user_speech)
    active_plan = engine.load_plan(f"{plan_name}.json")
    speak(f"Loaded plan: {active_plan.outcome.title}")

elif "next action" in user_speech.lower() or "what should i do" in user_speech.lower():
    if active_plan:
        next_actions = engine.get_next_actions(active_plan)
        if next_actions:
            speak(f"Your next action is: {next_actions[0].title}")
        else:
            speak("No actions available. All done or blocked.")
    else:
        speak("No plan loaded. Say 'load plan' first.")

elif "mark complete" in user_speech.lower():
    if active_plan:
        # Get the last mentioned step or ask which one
        step_id = get_last_mentioned_step_id()
        active_plan = engine.update_step(
            active_plan,
            step_id,
            status=StepStatus.COMPLETED
        )
        engine.save_plan(active_plan, f"{plan_name}.json")
        speak("Marked as complete!")
    else:
        speak("No active plan.")

elif "progress" in user_speech.lower():
    if active_plan:
        progress = engine.calculate_progress(active_plan)
        speak(f"You are {progress['percent']} percent complete. "
              f"{progress['completed']} steps done, {progress['not_started']} remaining.")
```

Now you can talk to your AI:
```
You: "Load my YouTube plan"
AI: "Loaded plan: Launch AI Tutorial YouTube Channel"

You: "What should I do next?"
AI: "Your next action is: Record first 5 tutorial videos"

You: "Mark it complete"
AI: "Marked as complete!"

You: "What's my progress?"
AI: "You are 24 percent complete. 5 steps done, 16 remaining."
```

---

## 6. Dashboard Integration (Web UI)

### Simple Flask Dashboard

Create `dashboard.py`:

```python
#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
import sys
sys.path.append('/home/panda/Documents/PythonScripts/OutcomeBackcasting')
from backcast_engine import BackcastEngine

app = Flask(__name__)
engine = BackcastEngine()

@app.route('/')
def index():
    plans = engine.list_plans()
    return render_template('dashboard.html', plans=plans)

@app.route('/api/plan/<filename>')
def get_plan(filename):
    plan = engine.load_plan(filename)
    progress = engine.calculate_progress(plan)
    next_actions = engine.get_next_actions(plan)

    return jsonify({
        'title': plan.outcome.title,
        'progress': progress,
        'next_actions': [
            {'id': a.id, 'title': a.title, 'priority': a.priority.value}
            for a in next_actions
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Access via browser: `http://localhost:5000`

---

## 7. CI/CD Integration

### GitHub Actions Workflow

`.github/workflows/backcast-update.yml`:

```yaml
name: Update Backcasting Plan

on:
  push:
    branches: [main]

jobs:
  update-plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Update deployment plan
        run: |
          python3 update_backcast.py \
            --plan deployment_plan.json \
            --step "Deploy to Production" \
            --status completed

      - name: Commit updated plan
        run: |
          git config user.name "GitHub Actions"
          git commit -am "Update deployment plan [skip ci]" || true
          git push
```

---

## Summary: Which Integration to Use?

| Your Goal | Best Integration | Why |
|-----------|------------------|-----|
| Daily personal planning | MCP + Claude Code | Natural language, AI assistance |
| Team collaboration | Notion/Asana sync | Team visibility, mobile access |
| Automation | Python scripts | Full control, custom logic |
| Voice planning | Voice chat integration | Hands-free, quick updates |
| Monitoring | Webhooks + Slack | Real-time notifications |
| Web access | Flask dashboard | Visual, accessible anywhere |
| DevOps | CI/CD integration | Auto-update from deployments |

---

**All these integrations work with the same core engine, so you can use multiple at once!**
