# Outcome Backcasting Engine

**Reverse-engineer your path from desired futures to present actions**

[![MCP Server](https://img.shields.io/badge/MCP-Server-blue)](https://modelcontextprotocol.io)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Author

**Derek M D Chan** — Creator and maintainer

*Co-developed with Claude (Anthropic)*

---

## Overview

The Outcome Backcasting Engine is a strategic planning tool that helps you work backwards from a desired future outcome to identify the specific steps, resources, and dependencies needed to achieve your goals. Unlike traditional forward planning, backcasting starts with your end goal and creates a reverse roadmap to get there.

## Key Concepts

### What is Backcasting?

Backcasting is a planning methodology that:
1. **Starts with the end in mind** - Define your desired future state
2. **Works backwards** - Identify what needs to happen to reach that state
3. **Creates actionable steps** - Break down the path into concrete actions
4. **Identifies dependencies** - Understand what must happen before other things
5. **Monitors progress** - Track advancement and adjust the plan dynamically

### When to Use Backcasting

- **Complex projects** with multiple phases and dependencies
- **Long-term goals** (6 months to several years)
- **Strategic initiatives** requiring coordination of many elements
- **Constraint-heavy scenarios** where certain requirements must be met
- **Innovation projects** where the path isn't immediately obvious

## Features

### Core Capabilities

- **Outcome Definition** - Clearly specify your desired end state
- **Automatic Step Generation** - Create template structures with major phases
- **Dependency Management** - Track which steps must be completed before others
- **Progress Tracking** - Monitor completion status across all steps
- **Risk Analysis** - Identify and plan for potential obstacles
- **Resource Planning** - Track required resources (time, money, skills, tools, people)
- **Critical Path Analysis** - Identify bottlenecks and longest dependency chains
- **Next Actions View** - See what's ready to be worked on right now

### Step Types

1. **Milestone** 🎯 - Major checkpoints marking significant progress
2. **Action** ⚡ - Concrete tasks to be executed
3. **Decision** 🤔 - Choice points requiring evaluation
4. **Dependency** 🔗 - External requirements or prerequisites
5. **Risk Mitigation** 🛡️ - Steps to reduce or eliminate risks

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

## Installation

### Prerequisites

- Python 3.7 or higher
- Linux environment (tested on openSUSE)

### Setup

1. The engine is located at:
   ```
   /home/panda/Documents/PythonScripts/OutcomeBackcasting/
   ```

2. Make the scripts executable:
   ```bash
   chmod +x /home/panda/Documents/PythonScripts/OutcomeBackcasting/*.sh
   chmod +x /home/panda/Documents/PythonScripts/OutcomeBackcasting/*.py
   ```

3. Run the launcher:
   ```bash
   ./run_backcast.sh
   ```

## Usage Guide

### Quick Start

1. **Launch the application:**
   ```bash
   ./run_backcast.sh
   ```

2. **Create a new plan** (Option 1):
   - Enter your outcome title (e.g., "Launch SaaS Product")
   - Describe what success looks like
   - Define success criteria (specific, measurable goals)
   - List constraints (budget, time, resources)
   - Set timeline (e.g., "9 months")

3. **Generate template steps** (optional):
   - Choose how many major phases (default: 5)
   - The engine creates a structured template
   - Customize the generated steps to fit your needs

4. **Customize your plan:**
   - Add specific steps for your project
   - Update descriptions and success criteria
   - Define dependencies between steps
   - Add resources and risk information

5. **Execute and track:**
   - View "Next Actions" to see what's ready to work on
   - Update step statuses as you make progress
   - Run analysis to get insights and suggestions
   - Export your plan to share or reference

### Menu Options

#### Plan Management

**1. Create new plan** - Start a fresh backcasting plan with wizard guidance

**2. Load existing plan** - Open a previously saved plan

**3. View plan overview** - See high-level summary, progress, and outcome details

#### View Steps

**4. View all steps** - List every step in the plan with status indicators

**5. View step details** - Deep dive into a specific step's information

**6. View next actions** - Show only steps that are ready to be worked on (all dependencies met)

**7. View critical path** - Identify the longest chain of dependencies (bottleneck analysis)

#### Edit Plan

**8. Add new step** - Create a custom step with full details

**9. Update step status** - Mark steps as completed, in progress, blocked, etc.

**10. Delete step** - Remove a step (dependencies are automatically cleaned up)

#### Analysis

**11. Analyze plan** - Get comprehensive analysis:
- Progress metrics (% complete, breakdown by status)
- Risk analysis (high-priority risks identified)
- Resource summary (grouped by type)
- Optimization suggestions (parallelization, bottlenecks)
- Current blockers (what's preventing progress)

**12. Export plan** - Save to different formats:
- **Markdown (.md)** - Rich formatting with emoji status indicators
- **Text (.txt)** - Simple plain text for universal compatibility
- **CSV (.csv)** - Spreadsheet format for Excel/Google Sheets

### Example Workflow

#### Scenario: Launching a New Product

```
OUTCOME: "Launch MVP of SaaS Analytics Platform"
TIMELINE: 6 months
SUCCESS CRITERIA:
  - 100 beta users signed up
  - Core features working (data ingestion, dashboards, alerts)
  - Payment processing integrated
  - Security audit passed

GENERATED PLAN (working backwards from launch):
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

## Advanced Features

### Dependency Management

Steps can depend on other steps. The engine automatically:
- Prevents working on steps with incomplete dependencies
- Shows "Next Actions" that are ready to start
- Identifies blocked steps and what's blocking them
- Calculates the critical path (longest dependency chain)

**Example:**
```
Step 5: "Deploy to Production"
  Dependencies: [3, 4]  # Requires Step 3 and 4 to be done first

Step 4: "Security Audit"
  Dependencies: [2]     # Requires Step 2

Step 3: "Beta Testing"
  Dependencies: [2]     # Requires Step 2

Step 2: "Feature Development"
  Dependencies: [1]     # Requires Step 1

Step 1: "Project Setup"
  Dependencies: []      # No dependencies, can start immediately
```

### Resource Tracking

Each step can specify required resources:

**Resource Types:**
- **Time** - How long it takes
- **Money** - Budget required
- **Skill** - Expertise needed
- **Tool** - Software, hardware, or equipment
- **Person** - Specific individuals or roles

**Example:**
```
Step: "Build Mobile App"
Resources:
  - Mobile Developer (person) - 2 developers
  - React Native (tool) - License required
  - 8 weeks (time) - Full-time work
  - $40,000 (money) - Contractor budget
  - iOS/Android expertise (skill) - Required
```

### Risk Management

Identify and mitigate potential problems:

**Risk Fields:**
- **Description** - What could go wrong
- **Probability** - Low, Medium, High
- **Impact** - Low, Medium, High
- **Mitigation** - How to prevent or handle it

**Example:**
```
Step: "Migrate to New Database"
Risk:
  Description: "Data loss during migration"
  Probability: Medium
  Impact: High
  Mitigation: "Create full backup, test migration on staging environment first,
               have rollback plan ready"
```

### Analysis Tools

**Progress Metrics:**
- Overall completion percentage
- Breakdown by status (completed, in progress, blocked)
- Visual indicators in CLI

**Critical Path Analysis:**
- Identifies longest dependency chain
- Highlights steps that will delay the entire project if delayed
- Helps prioritize work on bottlenecks

**Optimization Suggestions:**
- Identifies independent steps that could be parallelized
- Finds bottleneck steps with many dependents
- Flags steps without clear success criteria
- Highlights high risks without mitigation plans

**Blocker Detection:**
- Shows steps marked as "blocked"
- Lists which incomplete dependencies are causing the block
- Helps focus effort on unblocking critical work

## File Format

Plans are saved as JSON files in:
```
/home/panda/Documents/PythonScripts/OutcomeBackcasting/data/
```

**File Structure:**
```json
{
  "outcome": {
    "title": "...",
    "description": "...",
    "success_criteria": [...],
    "constraints": [...],
    "timeline": "..."
  },
  "steps": [
    {
      "id": 1,
      "title": "...",
      "description": "...",
      "type": "action",
      "status": "not_started",
      "priority": "high",
      "dependencies": [2, 3],
      "resources_needed": [...],
      "risks": [...],
      "success_criteria": [...]
    }
  ]
}
```

## Tips and Best Practices

### Defining Good Outcomes

**DO:**
- Be specific and measurable
- Include quantifiable success criteria
- Set realistic timelines
- Define what "done" looks like clearly

**DON'T:**
- Use vague language ("improve things")
- Set impossible goals without constraints
- Forget to define success criteria
- Skip the constraints section

### Creating Effective Steps

**DO:**
- Use action verbs (Build, Deploy, Test, Design)
- Make success criteria objective and testable
- Estimate durations realistically
- Identify all dependencies upfront
- Document risks as you think of them

**DON'T:**
- Create steps that are too large (break them down)
- Leave success criteria as "Define criteria"
- Forget to update status as work progresses
- Ignore potential risks

### Managing Dependencies

**Best Practices:**
- Review the critical path regularly
- Focus on unblocking high-priority items
- Look for opportunities to parallelize work
- Update dependencies as the plan evolves

### Using Next Actions

- Start each work session by checking "Next Actions"
- Focus on critical and high-priority items first
- Update status immediately when completing steps
- This keeps the plan current and useful

### Regular Analysis

**Weekly Review:**
- Run "Analyze plan" to check progress
- Review high-priority risks
- Check for new blockers
- Update step statuses

**Monthly Review:**
- Revisit the outcome - still accurate?
- Review optimization suggestions
- Adjust timeline if needed
- Clean up completed steps

## Command Reference

### Keyboard Shortcuts

- **Ctrl+D** or **END** - End multiline input
- **Ctrl+C** - Exit the program
- **Enter** - Continue after viewing results

### Input Formats

**Step IDs:**
- Single number: `5`
- Multiple (comma-separated): `1,3,5,7`

**Duration Format:**
- Use human-readable: `3 days`, `2 weeks`, `4 months`

**Priority/Status:**
- Select by number from menu

## Troubleshooting

### Common Issues

**"No plan loaded" error:**
- Create a new plan (Option 1) or load existing (Option 2) first

**Can't see next actions:**
- Check if dependencies are completed
- Review step statuses (might all be done or blocked)

**Plan file not found:**
- Check filename includes .json extension
- Verify file exists in data directory
- Use Option 2 to see list of available plans

**Dependencies not working:**
- Ensure step IDs are valid (match existing steps)
- Check for circular dependencies
- Verify dependent steps are actually completed

### Getting Help

- Re-read this README for detailed guidance
- Check the ai_plugin_concepts.md for design philosophy
- Review example workflows in this document

## Architecture

### Core Components

**backcast_engine.py** - Core engine with data models and algorithms
- Data classes (Outcome, Step, Resource, Risk, BackcastPlan)
- BackcastEngine class (CRUD operations, analysis)
- BackcastAnalyzer class (risk analysis, optimization suggestions)

**backcast_cli.py** - Interactive command-line interface
- BackcastCLI class (menu system, user interaction)
- Colored output for better UX
- Wizard-style plan creation
- Multiple view modes

**run_backcast.sh** - Launcher script
- Sets up environment
- Handles errors gracefully
- Unix line endings (LF)

### Data Flow

```
User Input → CLI → Engine → Data Storage (JSON)
                 ↓
             Analysis ← Analyzer
                 ↓
            Display Results
```

### Design Philosophy

Based on concept #9 from ai_plugin_concepts.md:

**Key Principles:**
1. **Outcome-first thinking** - Always start with the end goal
2. **Reverse planning** - Work backwards to find the path
3. **Constraint awareness** - Acknowledge limitations upfront
4. **Dynamic adjustment** - Plans evolve as work progresses
5. **Dependency clarity** - Make relationships explicit
6. **Risk consciousness** - Identify problems before they occur

## Future Enhancements

### Potential Features

- **AI-powered step generation** - Use LLM to suggest realistic steps
- **Timeline visualization** - Gantt chart style display
- **Collaborative planning** - Multi-user support
- **Integration with task managers** - Sync with Asana, Notion, etc.
- **Template library** - Pre-built plans for common goals
- **Monte Carlo simulation** - Probability-based timeline estimates
- **Notification system** - Alerts for blockers and deadlines
- **Mobile companion app** - Check status on the go
- **Web dashboard** - Visual progress tracking

### Integration Ideas

- **Project management tools** - Asana, Jira, Monday.com APIs
- **Calendar integration** - Auto-schedule steps based on dependencies
- **Team chat** - Slack/Discord notifications for status changes
- **Time tracking** - Toggl, Harvest integration for actual vs estimated
- **Document management** - Link steps to relevant files/docs

## Contributing

This is a personal utility built for local use. If you want to extend it:

1. Core engine is in `backcast_engine.py`
2. CLI interface is in `backcast_cli.py`
3. Data is stored in `data/` directory as JSON
4. Follow the existing code style (dataclasses, type hints, docstrings)

## Version History

**v1.0 - 2025-11-21**
- Initial release
- Core backcasting functionality
- Interactive CLI
- JSON storage
- Analysis tools
- Export to Markdown, Text, CSV

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author & Credits

**Derek M D Chan** — Creator and maintainer
- GitHub: [@NET-OF-BEING](https://github.com/NET-OF-BEING)

*Co-developed with Claude (Anthropic) using AI-assisted development*

---

**Built with the Outcome Backcasting methodology**

*Strategic planning tool that reverse-engineers paths from desired future outcomes to present actions.*
