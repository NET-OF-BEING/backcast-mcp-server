# Outcome Backcasting Engine - Integration Guide

The backcasting engine can be integrated into various platforms. This guide covers the available integration options.

## Overview of Integration Options

### 1. MCP Server (AI Assistants) ⭐ RECOMMENDED
Use the backcasting engine as a tool for AI assistants like Claude Code, ChatGPT, and custom AI agents.

### 2. REST API
Expose backcasting functionality via HTTP endpoints for web applications.

### 3. Python Library
Import directly into Python scripts and applications.

### 4. Project Management Tools
Sync with Asana, Notion, Jira, Monday.com, etc.

### 5. Calendar Integration
Auto-schedule steps based on dependencies and timelines.

---

## 1. MCP Server Integration (AI Tools)

### What is MCP?

**Model Context Protocol (MCP)** is a standard way for AI assistants to use external tools. It allows Claude Code, ChatGPT, and other AI systems to call your backcasting engine as a plugin.

### Features Available via MCP

When integrated, AI assistants can:
- Create new backcasting plans from natural language descriptions
- Load and analyze existing plans
- Get next actions and critical paths
- Update step statuses
- Add new steps dynamically
- Perform comprehensive analysis
- Save and export plans

### Setup for Claude Code

1. **Locate your Claude Code MCP config:**
   ```bash
   ~/.config/claude-code/mcp_settings.json
   ```

2. **Add the backcasting server:**
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

4. **Test it:**
   Ask Claude: "Use the backcast tool to create a plan for launching my podcast in 6 months"

### Available MCP Tools

| Tool Name | Description |
|-----------|-------------|
| `backcast_create_plan` | Create new plan from outcome description |
| `backcast_load_plan` | Load existing plan by filename |
| `backcast_list_plans` | List all saved plans |
| `backcast_get_overview` | Get plan summary and progress |
| `backcast_get_all_steps` | Get all steps (with optional details) |
| `backcast_get_next_actions` | Get ready-to-work-on steps |
| `backcast_get_critical_path` | Get longest dependency chain |
| `backcast_add_step` | Add new step to plan |
| `backcast_update_step_status` | Update step status |
| `backcast_analyze_plan` | Comprehensive analysis |
| `backcast_save_plan` | Save to JSON file |
| `backcast_export_markdown` | Export to Markdown |

### Example AI Conversations

**Creating a Plan:**
```
You: "Create a backcasting plan for writing a technical book in 12 months"

Claude: [Uses backcast_create_plan tool]
"I've created a plan with 5 major phases working backwards from publication:
Phase 5: Book published and promoted
Phase 4: Final editing and publishing
Phase 3: Peer review and revisions
Phase 2: Draft chapters written
Phase 1: Research and outline

Would you like me to show the next actions you should focus on?"
```

**Checking Progress:**
```
You: "What should I work on next for my book plan?"

Claude: [Uses backcast_load_plan + backcast_get_next_actions]
"Based on your current progress (32% complete), here are your next actions:
1. [CRITICAL] Complete Chapter 3 draft (estimated: 2 weeks)
2. [HIGH] Research case studies for Chapter 4
3. [MEDIUM] Set up technical review panel

Would you like me to update any of these when you complete them?"
```

**Analysis:**
```
You: "Analyze my startup launch plan and tell me if I'm on track"

Claude: [Uses backcast_analyze_plan]
"Analysis of your startup launch plan:

Progress: 45% complete (18/40 steps)
Timeline: 6 months → 3 months elapsed

⚠️ CONCERNS:
- 3 steps are blocked (need to resolve dependencies)
- Critical path shows 2 bottlenecks in MVP development
- High-risk item: No mitigation for API costs

✓ STRENGTHS:
- Marketing phase ahead of schedule
- All funding secured
- Strong team velocity

RECOMMENDATIONS:
1. Unblock Step 12 (API integration) immediately
2. Add risk mitigation for API costs
3. Consider parallelizing Steps 22 and 23
"
```

---

## 2. Python Library Integration

### Direct Import

Use the engine directly in Python scripts:

```python
from backcast_engine import (
    BackcastEngine, Outcome, Step,
    StepType, StepStatus, Priority
)

# Create engine
engine = BackcastEngine()

# Create outcome
outcome = Outcome(
    title="Launch SaaS Product",
    description="Build and launch with 1000 users",
    success_criteria=["1000 users", "Profitable"],
    constraints=["6 months", "$50k budget"],
    timeline="6 months"
)

# Create plan
plan = engine.create_plan(outcome)
plan = engine.generate_steps(plan, num_phases=5)

# Get next actions
next_actions = engine.get_next_actions(plan)
for action in next_actions:
    print(f"TODO: {action.title}")

# Update status
plan = engine.update_step(plan, step_id=1, status=StepStatus.COMPLETED)

# Save
engine.save_plan(plan, "my_saas_launch.json")
```

### Use Cases

- **Automated project management scripts**
- **CI/CD pipeline integration** (track deployment steps)
- **Custom dashboards** (web apps showing progress)
- **Batch processing** (analyze multiple plans)
- **Integration with other Python tools**

---

## 3. REST API (Web Applications)

### Creating a REST API Server

Create `api_server.py`:

```python
#!/usr/bin/env python3
from flask import Flask, request, jsonify
from backcast_engine import BackcastEngine, Outcome, Step
# ... implement REST endpoints

app = Flask(__name__)
engine = BackcastEngine()

@app.route('/api/plans', methods=['POST'])
def create_plan():
    data = request.json
    # Create plan from JSON data
    # Return plan ID

@app.route('/api/plans/<plan_id>', methods=['GET'])
def get_plan(plan_id):
    # Load and return plan

@app.route('/api/plans/<plan_id>/next-actions', methods=['GET'])
def get_next_actions(plan_id):
    # Return next actions

# ... more endpoints
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/plans` | POST | Create new plan |
| `/api/plans` | GET | List all plans |
| `/api/plans/<id>` | GET | Get plan details |
| `/api/plans/<id>/steps` | GET | Get all steps |
| `/api/plans/<id>/next-actions` | GET | Get next actions |
| `/api/plans/<id>/analyze` | GET | Analyze plan |
| `/api/steps` | POST | Add step |
| `/api/steps/<id>` | PATCH | Update step |

---

## 4. Project Management Tool Integration

### Notion Integration

```python
# Export plan to Notion database
from notion_client import Client

notion = Client(auth=os.environ["NOTION_TOKEN"])

# Create database for plan
database = notion.databases.create(
    parent={"page_id": page_id},
    title=[{"text": {"content": plan.outcome.title}}],
    properties={
        "Name": {"title": {}},
        "Status": {"select": {}},
        "Priority": {"select": {}},
        "Dependencies": {"rich_text": {}}
    }
)

# Add steps as pages
for step in plan.steps:
    notion.pages.create(
        parent={"database_id": database["id"]},
        properties={
            "Name": {"title": [{"text": {"content": step.title}}]},
            "Status": {"select": {"name": step.status.value}},
            # ... more properties
        }
    )
```

### Asana Integration

```python
import asana

client = asana.Client.access_token('YOUR_TOKEN')

# Create project
project = client.projects.create_in_workspace(
    workspace_gid,
    {"name": plan.outcome.title}
)

# Create tasks from steps
for step in plan.steps:
    client.tasks.create({
        "name": step.title,
        "notes": step.description,
        "projects": [project["gid"]]
    })
```

### Integration Benefits

- **Two-way sync**: Update statuses in PM tool, reflect in backcasting engine
- **Team collaboration**: Share plans with team
- **Rich features**: Use PM tool's commenting, attachments, etc.
- **Mobile access**: Use PM tool's mobile apps

---

## 5. Calendar Integration

### Google Calendar Sync

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Authenticate
creds = Credentials.from_authorized_user_file('token.json')
service = build('calendar', 'v3', credentials=creds)

# Schedule steps based on dependencies
for step in plan.steps:
    if not step.dependencies:  # Can start immediately
        event = {
            'summary': step.title,
            'description': step.description,
            'start': {'date': calculate_start_date(step)},
            'end': {'date': calculate_end_date(step)}
        }
        service.events().insert(calendarId='primary', body=event).execute()
```

### Smart Scheduling

- Calculate start dates based on dependencies
- Respect constraints (working hours, weekends)
- Auto-adjust when steps complete early/late
- Send reminders for upcoming milestones

---

## 6. Webhook Integration

### Real-time Updates

Create a webhook server that notifies external systems when plans change:

```python
import requests

def on_step_completed(plan, step):
    """Called when step status changes to completed"""
    webhook_url = "https://your-app.com/webhooks/backcast"
    requests.post(webhook_url, json={
        "event": "step_completed",
        "plan_id": plan.outcome.title,
        "step_id": step.id,
        "step_title": step.title,
        "progress": engine.calculate_progress(plan)
    })
```

### Use Cases

- Slack/Discord notifications
- Trigger CI/CD pipelines
- Update dashboards
- Send emails
- Log to analytics

---

## 7. Voice Assistant Integration

### Integrate with Your Voice Chat

Modify `/home/panda/voice_chat.py` to include backcasting commands:

```python
# In voice_chat.py, add command handling:

if "what's my next action" in user_speech.lower():
    # Load active plan
    plan = engine.load_plan("active_plan.json")
    next_actions = engine.get_next_actions(plan)

    response = "Your next actions are: "
    for action in next_actions[:3]:
        response += f"{action.title}. "

    speak(response)

elif "update step" in user_speech.lower():
    # Parse step ID and new status
    # Update in backcasting engine
    # Confirm via voice
```

---

## Integration Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Backcasting Engine Core                │
│              (backcast_engine.py)                       │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  MCP Server  │    │  REST API    │    │ Python Lib   │
│ (AI Tools)   │    │ (Web Apps)   │    │ (Scripts)    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Claude Code  │    │ Dashboards   │    │ Automation   │
│ ChatGPT      │    │ Mobile Apps  │    │ CI/CD        │
│ Custom AIs   │    │ Websites     │    │ Monitoring   │
└──────────────┘    └──────────────┘    └──────────────┘

        Plus External Integrations:
        ↓
┌─────────────────────────────────────────────────────────┐
│  Notion • Asana • Jira • Google Calendar • Slack       │
│  Discord • Email • Webhooks • Analytics                 │
└─────────────────────────────────────────────────────────┘
```

---

## Best Integration for Different Scenarios

### Scenario 1: Personal Planning (Solo Developer)
**Best Choice:** MCP Server + Claude Code
- Natural language interaction
- AI suggests next steps
- Quick updates via chat
- No infrastructure needed

### Scenario 2: Team Project Management
**Best Choice:** Notion/Asana Integration
- Team visibility
- Collaboration features
- Mobile access
- Comments and attachments

### Scenario 3: Automated Workflows
**Best Choice:** Python Library + Webhooks
- Direct control
- Custom logic
- Integration with existing systems
- Event-driven updates

### Scenario 4: Web Application
**Best Choice:** REST API
- Multi-user support
- Web dashboard
- Mobile apps
- Scalable architecture

### Scenario 5: Voice-First Planning
**Best Choice:** Voice Assistant Integration
- Hands-free updates
- Quick status checks
- Natural interaction
- Great for mobile users

---

## Getting Started

### Quick Start: MCP Integration

1. **Enable MCP Server:**
   ```bash
   chmod +x mcp_server.py
   ```

2. **Add to Claude Code config:**
   ```bash
   # Copy mcp_config.json content to your Claude Code settings
   ```

3. **Test it:**
   ```
   Ask Claude: "List my backcasting plans"
   ```

### Quick Start: Python Library

```python
# In your Python script
import sys
sys.path.append('/home/panda/Documents/PythonScripts/OutcomeBackcasting')

from backcast_engine import BackcastEngine

engine = BackcastEngine()
# Use it!
```

---

## Support & Resources

- **Core Documentation:** `README.md`
- **Quick Start Guide:** `QUICKSTART.md`
- **MCP Server Code:** `mcp_server.py`
- **Example Plan:** `data/example_ai_assistant_launch.json`

---

**The backcasting engine is designed to be a plugin-ready system that can integrate anywhere you need strategic planning capabilities!**
