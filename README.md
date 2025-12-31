# Outcome Backcasting MCP Server

**Reverse-engineer your path from desired futures to present actions**

![MCP Server](https://img.shields.io/badge/MCP-Server-blue) ![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Author
**Derek M D Chan** — Creator and maintainer  
Co-developed with Claude (Anthropic)

---

## Overview

The **Outcome Backcasting MCP Server** exposes strategic planning capabilities to Claude through the Model Context Protocol (MCP). This allows Claude to help users plan complex projects by working backwards from desired outcomes to identify concrete steps, dependencies, and resources needed.

Unlike traditional forward planning tools, this MCP server enables Claude to:
- **Start with the end in mind** - Help users define their desired future state
- **Work backwards** - Identify what needs to happen to reach that state
- **Create actionable roadmaps** - Break down the path into concrete, sequenced steps
- **Manage dependencies** - Understand and track what must happen before other things
- **Monitor progress** - Track advancement and suggest adjustments dynamically

### What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open standard that enables AI assistants like Claude to securely connect with external tools and data sources. This backcasting server implements MCP, allowing Claude to:

- Access and manipulate backcasting plans on your behalf
- Analyze project dependencies and critical paths
- Provide strategic planning guidance with real data
- Track progress across complex, multi-phase projects

---

## Key Concepts

### What is Backcasting?

Backcasting is a planning methodology that:

1. **Starts with the end in mind** - Define your desired future state
2. **Works backwards** - Identify what needs to happen to reach that state
3. **Creates actionable steps** - Break down the path into concrete actions
4. **Identifies dependencies** - Understand what must happen before other things
5. **Monitors progress** - Track advancement and adjust the plan dynamically

### When Claude Uses Backcasting

Through this MCP server, Claude can help you with:

- **Complex projects** with multiple phases and dependencies
- **Long-term goals** (6 months to several years)
- **Strategic initiatives** requiring coordination of many elements
- **Constraint-heavy scenarios** where certain requirements must be met
- **Innovation projects** where the path isn't immediately obvious

---

## MCP Server Capabilities

### Core Tools Exposed to Claude

When you connect this MCP server to Claude, it gains access to these planning capabilities:

#### Plan Management Tools
- **`create_plan`** - Create a new backcasting plan with outcome definition
- **`load_plan`** - Load an existing plan from storage
- **`get_plan_overview`** - Retrieve high-level summary and progress metrics
- **`list_plans`** - Show all available saved plans

#### Step Management Tools
- **`add_step`** - Add a new step to the plan with full details
- **`update_step_status`** - Mark steps as completed, in progress, blocked, etc.
- **`delete_step`** - Remove a step (dependencies automatically cleaned up)
- **`get_step_details`** - Retrieve comprehensive information about a specific step

#### View Tools
- **`list_all_steps`** - Get all steps in the plan with status indicators
- **`get_next_actions`** - Show steps ready to work on (dependencies met)
- **`get_critical_path`** - Identify the longest dependency chain
- **`get_blocked_steps`** - Find steps that cannot proceed and why

#### Analysis Tools
- **`analyze_plan`** - Get comprehensive analysis including:
  - Progress metrics (% complete, breakdown by status)
  - Risk analysis (high-priority risks identified)
  - Resource summary (grouped by type)
  - Optimization suggestions (parallelization, bottlenecks)
  - Current blockers (what's preventing progress)

#### Export Tools
- **`export_plan`** - Export to multiple formats:
  - **Markdown** (.md) - Rich formatting with emoji status indicators
  - **Text** (.txt) - Simple plain text for universal compatibility
  - **CSV** (.csv) - Spreadsheet format for Excel/Google Sheets

---

## Data Structures

### Step Types

The MCP server recognizes these step types:

- **Milestone** 🎯 - Major checkpoints marking significant progress
- **Action** ⚡ - Concrete tasks to be executed
- **Decision** 🤔 - Choice points requiring evaluation
- **Dependency** 🔗 - External requirements or prerequisites
- **Risk Mitigation** 🛡️ - Steps to reduce or eliminate risks

### Priority Levels

- **Critical** 🔴 - Must be done, no alternatives
- **High** 🟠 - Very important, high impact
- **Medium** 🟡 - Important but not urgent
- **Low** ⚪ - Nice to have, low priority

### Status Tracking

- **Not Started** - Step hasn't been begun yet
- **In Progress** - Currently being worked on
- **Completed** - Successfully finished
- **Blocked** - Cannot proceed due to dependencies
- **Skipped** - Decided not to pursue this step

### Resource Types

Each step can specify required resources:

- **Time** - Duration estimates
- **Money** - Budget requirements
- **Skill** - Expertise needed
- **Tool** - Software, hardware, or equipment
- **Person** - Specific individuals or roles

---

## Installation

### Prerequisites

- Python 3.7 or higher
- Linux environment (tested on openSUSE)
- **Claude Desktop app** OR **Claude Code CLI** (or both!)

### Which Claude Client Should You Use?

| Use Case | Recommended Client |
|----------|-------------------|
| **Strategic planning & brainstorming** | Claude Desktop (GUI) |
| **Visual roadmaps & artifacts** | Claude Desktop (GUI) |
| **General project planning** | Claude Desktop (GUI) |
| **Planning during coding sessions** | Claude Code (CLI) |
| **Automated plan updates** | Claude Code (CLI) |
| **Technical project management** | Either (personal preference) |

**Both clients can use the same MCP server!** You can configure it for both and switch between them as needed.

### Setup

1. **Navigate to the installation directory:**
   ```bash
   cd /home/panda/Documents/PythonScripts/OutcomeBackcasting/
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x *.sh *.py
   ```

3. **Configure your Claude client to use this MCP server:**

   ### For Claude Desktop:
   
   Add to your Claude Desktop config file:
   - **macOS/Linux:** `~/.config/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "outcome-backcasting": {
         "command": "/home/panda/Documents/PythonScripts/OutcomeBackcasting/run_backcast_mcp.sh"
       }
     }
   }
   ```

   ### For Claude Code:
   
   Add to your Claude Code config file: `~/.claude/config.json`

   ```json
   {
     "mcpServers": {
       "outcome-backcasting": {
         "command": "/home/panda/Documents/PythonScripts/OutcomeBackcasting/run_backcast_mcp.sh"
       }
     }
   }
   ```

   **Note:** On Windows, adjust the path to use Windows-style paths:
   ```json
   {
     "mcpServers": {
       "outcome-backcasting": {
         "command": "C:\\Users\\YourName\\Documents\\PythonScripts\\OutcomeBackcasting\\run_backcast_mcp.sh"
       }
     }
   }
   ```

4. **Restart your Claude client** to load the MCP server
   - **Claude Desktop:** Fully quit and reopen the app
   - **Claude Code:** Restart your terminal session or run `claude configure`

5. **Verify connection** by asking Claude:
   ```
   "Can you help me create a backcasting plan?"
   ```
   
   Claude should acknowledge it has access to backcasting tools.

---

## Usage Through Claude

### How to Interact

Instead of using a command-line interface directly, you interact with the backcasting engine **through Claude**. Simply talk to Claude naturally about your project planning needs.

The experience differs slightly between clients:

### Claude Desktop (GUI) Usage

Best for: Strategic planning, brainstorming, visual roadmaps

**You:** "I want to create a backcasting plan for launching a SaaS product in 9 months."

**Claude:** Creates an artifact with your plan overview, asks clarifying questions interactively, and displays visual progress indicators.

**Benefits:**
- ✅ Rich artifacts with formatted roadmaps
- ✅ Easy to review and reference plans visually
- ✅ Better for collaborative planning sessions
- ✅ Natural conversation flow with context

### Claude Code (CLI) Usage

Best for: Technical planning, automation, coding workflows

```bash
$ claude "Create a backcasting plan for refactoring the authentication system"
```

**Claude:** Generates the plan, saves it to a file, and shows next actions in terminal-friendly format.

**Benefits:**
- ✅ Integrate planning into development workflow
- ✅ Automate plan updates via scripts
- ✅ Quick status checks during coding
- ✅ Works in headless/server environments

### Example Conversations

#### Creating a New Plan

**You:** "I want to create a backcasting plan for launching a SaaS product in 9 months."

**Claude:** Uses the `create_plan` tool to set up your project, then asks clarifying questions about:
- What success looks like
- Specific success criteria
- Budget and timeline constraints
- Key phases and milestones

#### Viewing Progress

**You:** "What's the current status of my product launch plan?"

**Claude:** Uses `get_plan_overview` and `analyze_plan` tools to show:
- Overall completion percentage
- Steps in progress vs completed
- Critical risks
- Next recommended actions

#### Getting Next Actions

**You:** "What should I work on next?"

**Claude:** Uses `get_next_actions` tool to show steps where:
- All dependencies are complete
- Status is "not started" or "in progress"
- Prioritized by importance

#### Identifying Bottlenecks

**You:** "What's blocking my progress?"

**Claude:** Uses `get_blocked_steps` and `get_critical_path` tools to identify:
- Steps marked as blocked
- Which dependencies are causing blocks
- The longest dependency chain affecting timeline

---

## Example Workflow Through Claude

### Scenario: Launching a New Product

**You:** "I need to plan the launch of an MVP for a SaaS analytics platform in 6 months."

**Claude:** "I'll help you create a backcasting plan. Let me ask a few questions to define your outcome..."

*(Claude uses `create_plan` tool)*

**Claude:** "What does success look like for this launch?"

**You:** "100 beta users signed up, core features working, payment processing integrated, security audit passed."

**Claude:** "Got it. I'll generate a reverse roadmap from that outcome. Based on your 6-month timeline, I'm creating 5 major phases working backwards from launch..."

*(Claude uses `add_step` tool multiple times)*

**Generated Plan Structure:**

```
[Phase 5] Public Launch
  → Beta testing complete
  → All critical bugs fixed
  → Marketing materials ready

[Phase 4] Beta Testing
  → 50 beta users onboarded
  → Feedback loop established
  → Rapid iteration process

[Phase 3] Core Features Complete
  → Dashboard system working
  → Data pipeline stable
  → Alert system functional

[Phase 2] Technical Foundation
  → Database architecture finalized
  → API endpoints created
  → Authentication system built

[Phase 1] Project Setup
  → Tech stack chosen
  → Development environment configured
  → Team assembled
```

**You:** "What should I start working on?"

**Claude:** *(uses `get_next_actions` tool)* "Based on your dependencies, here are the steps you can start immediately..."

**You:** "I just completed the tech stack selection. Update the plan."

**Claude:** *(uses `update_step_status` tool)* "Great! I've marked that step complete. This unlocks 3 new actions you can now start..."

---

## MCP Tool Reference

### Plan Management

#### `create_plan`
**Parameters:**
- `title` (string) - Name of the outcome
- `description` (string) - Detailed description of desired end state
- `success_criteria` (array) - List of measurable success indicators
- `constraints` (array) - Budget, time, resource limitations
- `timeline` (string) - Expected duration (e.g., "9 months")

**Returns:** Plan ID and confirmation

#### `load_plan`
**Parameters:**
- `plan_name` (string) - Name of saved plan file

**Returns:** Complete plan object with all steps

#### `get_plan_overview`
**Parameters:**
- `plan_id` (string) - ID of the plan

**Returns:**
- Outcome details
- Progress metrics
- Step count breakdown
- Timeline information

### Step Operations

#### `add_step`
**Parameters:**
- `plan_id` (string) - Plan to add step to
- `title` (string) - Step name
- `description` (string) - Detailed information
- `type` (enum) - milestone, action, decision, dependency, risk_mitigation
- `priority` (enum) - critical, high, medium, low
- `dependencies` (array) - IDs of prerequisite steps
- `resources` (array) - Required resources
- `risks` (array) - Potential risks
- `success_criteria` (array) - How to know step is complete

**Returns:** New step ID

#### `update_step_status`
**Parameters:**
- `plan_id` (string)
- `step_id` (integer)
- `status` (enum) - not_started, in_progress, completed, blocked, skipped

**Returns:** Updated step object

#### `get_step_details`
**Parameters:**
- `plan_id` (string)
- `step_id` (integer)

**Returns:** Complete step information including dependencies, resources, risks

### View Operations

#### `list_all_steps`
**Parameters:**
- `plan_id` (string)

**Returns:** Array of all steps with status indicators

#### `get_next_actions`
**Parameters:**
- `plan_id` (string)

**Returns:** Steps that are:
- Not completed/skipped
- All dependencies met
- Sorted by priority

#### `get_critical_path`
**Parameters:**
- `plan_id` (string)

**Returns:** Longest dependency chain through the plan (bottleneck path)

#### `get_blocked_steps`
**Parameters:**
- `plan_id` (string)

**Returns:** Steps marked as blocked with dependency details

### Analysis

#### `analyze_plan`
**Parameters:**
- `plan_id` (string)

**Returns:**
- **Progress metrics:** % complete, status breakdown
- **Risk analysis:** High-priority risks
- **Resource summary:** Grouped by type
- **Optimization suggestions:** Parallelization opportunities, bottlenecks
- **Current blockers:** What's preventing progress

### Export

#### `export_plan`
**Parameters:**
- `plan_id` (string)
- `format` (enum) - markdown, text, csv
- `output_path` (string) - Where to save file

**Returns:** File path and success confirmation

---

## Advanced Features

### Dependency Management

Claude can help you manage complex dependencies automatically:

- **Prevents invalid states** - Can't complete a step if dependencies aren't done
- **Shows ready actions** - Identifies what's unblocked and ready to start
- **Tracks blockers** - Explains why certain steps can't proceed
- **Calculates critical path** - Finds the bottleneck chain

**Example:**

**You:** "I want to deploy to production."

**Claude:** *(checks dependencies)* "That step requires the security audit (Step 4) and beta testing (Step 3) to be complete first. Currently, only project setup (Step 1) is done. You need to finish Steps 2, 3, and 4 before deployment."

### Resource Tracking

Each step tracks multiple resource types:

**Example:**

**You:** "What resources do I need for the mobile app development step?"

**Claude:** *(uses `get_step_details`)* 
```
Step: "Build Mobile App"
Resources Required:
  - Person: 2 Mobile Developers
  - Tool: React Native license
  - Time: 8 weeks full-time
  - Money: $40,000 contractor budget
  - Skill: iOS/Android expertise required
```

### Risk Management

Identify and plan for potential problems:

**Example:**

**You:** "What are the biggest risks in my database migration step?"

**Claude:** *(analyzes risks)*
```
Step: "Migrate to New Database"
High-Priority Risk:
  Description: Data loss during migration
  Probability: Medium
  Impact: High
  Mitigation: Create full backup, test on staging first, 
              have rollback plan ready
```

### Analysis Tools

#### Progress Metrics
Claude can show you:
- Overall completion percentage
- Breakdown by status
- Velocity trends over time

#### Critical Path Analysis
- Identifies longest dependency chain
- Highlights steps that will delay the entire project if delayed
- Helps prioritize work on bottlenecks

#### Optimization Suggestions
Claude can identify:
- Independent steps that could be parallelized
- Bottleneck steps with many dependents
- Steps without clear success criteria
- High risks without mitigation plans

#### Blocker Detection
- Shows steps marked as "blocked"
- Lists which incomplete dependencies are causing the block
- Helps focus effort on unblocking critical work

---

## Data Storage

### File Format

Plans are stored as JSON files in:
```
/home/panda/Documents/PythonScripts/OutcomeBackcasting/data/
```

### Structure Example

```json
{
  "outcome": {
    "title": "Launch SaaS Product",
    "description": "Successfully launch MVP to market",
    "success_criteria": [
      "100 beta users signed up",
      "Core features working",
      "Payment processing integrated"
    ],
    "constraints": [
      "Budget: $50,000",
      "Timeline: 6 months",
      "Team: 3 developers"
    ],
    "timeline": "6 months"
  },
  "steps": [
    {
      "id": 1,
      "title": "Project Setup",
      "description": "Initialize project infrastructure",
      "type": "action",
      "status": "completed",
      "priority": "critical",
      "dependencies": [],
      "resources_needed": [
        {
          "type": "person",
          "description": "Project Manager",
          "quantity": 1
        }
      ],
      "risks": [],
      "success_criteria": [
        "Repository created",
        "Team onboarded"
      ]
    }
  ]
}
```

---

## Tips for Effective Use Through Claude

### Defining Good Outcomes

**Effective prompts to Claude:**

✅ **DO:**
- "I want to launch a product with 100 users, $50k revenue, and positive reviews in 9 months"
- "Help me plan to get promoted to senior engineer by meeting these criteria..."
- "Create a plan to lose 30 pounds in 6 months through diet and exercise"

❌ **DON'T:**
- "I want to be successful" (too vague)
- "Help me with my project" (no specifics)
- "Make a plan for everything" (no scope)

### Working with Claude on Steps

**Good requests:**

✅ "Add a step for building the authentication system with dependencies on the database setup"
✅ "Show me what's ready to work on that's high priority"
✅ "What risks should I be aware of in the deployment phase?"

**Natural conversation:**

**You:** "I just hired a designer."

**Claude:** "Great! That unblocks the UI design step. Would you like me to update that step's status to 'in progress'?"

### Regular Check-ins

**Weekly:**
- "What's my progress on the product launch plan?"
- "What should I focus on this week?"
- "Are there any new blockers?"

**Monthly:**
- "Analyze my plan and give me optimization suggestions"
- "What's on the critical path that could delay the project?"
- "Do I need to adjust my timeline?"

---

## Troubleshooting

### Common Issues

**"I don't see the backcasting tools in Claude Desktop"**
- Verify MCP server is configured in `claude_desktop_config.json`
- Check config file syntax (valid JSON)
- Restart Claude Desktop completely (Quit, not just close window)
- Check that the server script has execute permissions: `chmod +x run_backcast_mcp.sh`
- Look for errors in Claude Desktop logs

**"I don't see the backcasting tools in Claude Code"**
- Verify MCP server is configured in `~/.claude/config.json`
- Run `claude configure` to reload config
- Check that the server script path is absolute, not relative
- Test the server script manually: `./run_backcast_mcp.sh`
- Check Claude Code logs with `--verbose` flag

**"Claude says it can't access my plan"**
- Ask Claude to list available plans: "What backcasting plans do I have?"
- Verify the plan file exists in the data directory: `ls /home/panda/Documents/PythonScripts/OutcomeBackcasting/data/`
- Check file permissions on the data directory
- Try loading by exact filename: "Load my plan called 'product-launch.json'"

**"MCP server keeps disconnecting"**
- Check that `run_backcast_mcp.sh` has proper error handling
- Verify Python environment is accessible
- Test server independently before connecting to Claude
- Check system logs for Python errors

**"Dependencies seem wrong"**
- Ask Claude to show the critical path
- Request a dependency graph visualization
- Have Claude check for circular dependencies

**"Plan isn't updating"**
- Confirm Claude is using the correct plan ID
- Ask Claude to reload the plan from disk
- Check file permissions on the data directory
- Verify no other process is locking the JSON file

**"Config file location unclear"**

**For Claude Desktop:**
- macOS: `~/.config/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**For Claude Code:**
- All platforms: `~/.claude/config.json`

### Getting Help Through Claude

Simply ask Claude naturally:
- "How does this backcasting system work?"
- "Can you explain what the critical path means?"
- "Show me an example of a good project plan"
- "What information do you need to create a plan for me?"

---

## Architecture

### MCP Server Components

```
OutcomeBackcasting/
├── backcast_engine.py       # Core data models and business logic
├── backcast_mcp_server.py   # MCP protocol implementation
├── run_backcast_mcp.sh      # Server launcher for Claude
├── data/                    # JSON plan storage
│   ├── example-plan.json
│   └── my-project.json
└── README.md               # This file
```

### How MCP Integration Works

1. **Claude Desktop** connects to the MCP server on startup
2. **User asks Claude** a planning-related question
3. **Claude decides** which MCP tool to call based on context
4. **MCP server** executes the requested operation
5. **Results return** to Claude
6. **Claude presents** information naturally to the user

### Data Flow

```
User ←→ Claude (MCP Client)
           ↕
    MCP Protocol (stdio)
           ↕
   Backcast MCP Server
           ↕
    Engine (backcast_engine.py)
           ↕
    File System (JSON storage)
```

---

## Design Philosophy

Based on concept #9 from `ai_plugin_concepts.md`:

### Key Principles

1. **Outcome-first thinking** - Always start with the end goal
2. **Reverse planning** - Work backwards to find the path
3. **Constraint awareness** - Acknowledge limitations upfront
4. **Dynamic adjustment** - Plans evolve as work progresses
5. **Dependency clarity** - Make relationships explicit
6. **Risk consciousness** - Identify problems before they occur
7. **AI-assisted planning** - Leverage Claude's reasoning with real data

### MCP-Specific Benefits

- **Contextual awareness** - Claude sees your entire conversation history
- **Natural interaction** - No need to learn command syntax
- **Intelligent defaults** - Claude suggests reasonable values
- **Proactive analysis** - Claude can notice patterns and offer insights
- **Multi-plan management** - Claude can compare and contrast different plans

---

## Future Enhancements

### Planned Features

- **Visualization generation** - Gantt charts, dependency graphs
- **Timeline predictions** - Monte Carlo simulation for completion dates
- **Template library** - Pre-built plans for common goals
- **Collaborative features** - Multi-user plan editing
- **Integration APIs** - Connect with Asana, Jira, Notion
- **Notification system** - Alerts for blockers and deadlines
- **Version control** - Track plan changes over time
- **AI-powered suggestions** - Use LLM to generate realistic step sequences

### Integration Opportunities

With other MCP servers:
- **Calendar** - Auto-schedule steps based on dependencies
- **File system** - Link steps to relevant documents
- **Project management** - Sync with external tools
- **Time tracking** - Compare estimated vs actual time
- **Communication** - Notify team via Slack/Discord

---

## Contributing

This MCP server is designed for personal use but can be extended:

- **Core engine:** `backcast_engine.py`
- **MCP implementation:** `backcast_mcp_server.py`
- **Data format:** JSON files in `data/`
- **Code style:** Dataclasses, type hints, docstrings

To add new tools:
1. Add function to `backcast_mcp_server.py`
2. Register in MCP tool manifest
3. Update this README with tool documentation

---

## Version History

**v1.0** - 2025-01-01
- Initial MCP server release
- Core backcasting functionality
- Full CRUD operations on plans and steps
- Analysis and export tools
- JSON-based storage
- Integration with Claude Desktop

---

## License

MIT License - Free to use and modify

---

## Author & Credits

**Derek M D Chan** — Creator and maintainer

GitHub: [@NET-OF-BEING](https://github.com/NET-OF-BEING)

Co-developed with **Claude (Anthropic)** using AI-assisted development

Built on the **Outcome Backcasting** methodology: Strategic planning that reverse-engineers paths from desired future outcomes to present actions, now accessible through natural conversation with Claude via the Model Context Protocol.

---

## Quick Start Summary

### For Claude Desktop Users:

1. **Configure** in `~/.config/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "outcome-backcasting": {
         "command": "/home/panda/Documents/PythonScripts/OutcomeBackcasting/run_backcast_mcp.sh"
       }
     }
   }
   ```

2. **Restart** Claude Desktop
3. **Ask Claude:** "Help me create a backcasting plan for [your goal]"
4. **Collaborate** with Claude through natural conversation
5. **View** rich artifacts with formatted roadmaps

### For Claude Code Users:

1. **Configure** in `~/.claude/config.json`:
   ```json
   {
     "mcpServers": {
       "outcome-backcasting": {
         "command": "/home/panda/Documents/PythonScripts/OutcomeBackcasting/run_backcast_mcp.sh"
       }
     }
   }
   ```

2. **Reload** config with `claude configure` or restart terminal
3. **Use inline:** `claude "Create a backcasting plan for [goal]"`
4. **Track progress:** `claude "What should I work on next for my [project] plan?"`
5. **Automate:** Integrate into build scripts or CI/CD

### Universal Workflow:

1. **Define outcome** with success criteria and constraints
2. **Generate plan** working backwards from the goal
3. **Execute** by asking for next actions regularly
4. **Track progress** through natural conversation
5. **Adjust** as circumstances change

**The power of backcasting + the intelligence of Claude = Strategic planning made simple.**
