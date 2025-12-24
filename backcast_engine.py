#!/usr/bin/env python3
"""
Outcome Backcasting Engine
Reverse-engineers paths from desired futures to present actions
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from io import BytesIO

# Optional imports for enhanced features
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from icalendar import Calendar, Event
    HAS_ICALENDAR = True
except ImportError:
    HAS_ICALENDAR = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class StepStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class StepType(Enum):
    MILESTONE = "milestone"
    ACTION = "action"
    DECISION = "decision"
    DEPENDENCY = "dependency"
    RISK_MITIGATION = "risk_mitigation"


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Resource:
    """Represents a resource needed for a step"""
    name: str
    type: str  # time, money, skill, tool, person
    amount: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Risk:
    """Represents a potential risk"""
    description: str
    probability: str  # low, medium, high
    impact: str  # low, medium, high
    mitigation: str


@dataclass
class Step:
    """Represents a single step in the backcast path"""
    id: int
    title: str
    description: str
    type: StepType
    priority: Priority
    status: StepStatus
    estimated_duration: Optional[str]
    resources_needed: List[Resource]
    dependencies: List[int]  # IDs of steps that must be completed first
    success_criteria: List[str]
    risks: List[Risk]
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    completed_at: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


@dataclass
class Outcome:
    """Represents the desired future outcome"""
    title: str
    description: str
    success_criteria: List[str]
    constraints: List[str]
    timeline: str
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class BackcastPlan:
    """Complete backcasting plan"""
    outcome: Outcome
    steps: List[Step]
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class BackcastEngine:
    """Main engine for outcome backcasting"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/Documents/PythonScripts/OutcomeBackcasting/data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def create_plan(self, outcome: Outcome) -> BackcastPlan:
        """Create a new backcasting plan"""
        return BackcastPlan(outcome=outcome, steps=[])

    def generate_steps(self, plan: BackcastPlan, num_major_phases: int = 5) -> BackcastPlan:
        """
        Generate backward steps from outcome to present.
        This is a framework - users will customize the actual steps.
        """
        steps = []
        step_id = 1

        # Phase 0: Outcome Achievement (the final milestone)
        steps.append(Step(
            id=step_id,
            title=f"Achieve: {plan.outcome.title}",
            description=plan.outcome.description,
            type=StepType.MILESTONE,
            priority=Priority.CRITICAL,
            status=StepStatus.NOT_STARTED,
            estimated_duration=None,
            resources_needed=[],
            dependencies=[],
            success_criteria=plan.outcome.success_criteria,
            risks=[],
            notes="This is your final outcome. All other steps lead here."
        ))
        step_id += 1

        # Generate placeholder phases working backwards
        previous_step_id = 1
        for phase in range(num_major_phases, 0, -1):
            # Create a milestone for this phase
            milestone_step = Step(
                id=step_id,
                title=f"Phase {phase} Complete",
                description=f"Major milestone in phase {phase}",
                type=StepType.MILESTONE,
                priority=Priority.HIGH,
                status=StepStatus.NOT_STARTED,
                estimated_duration="2-4 weeks",
                resources_needed=[],
                dependencies=[step_id + 1] if phase < num_major_phases else [previous_step_id],
                success_criteria=["Define specific criteria"],
                risks=[],
                notes=f"Define what 'done' looks like for phase {phase}"
            )
            steps.append(milestone_step)
            milestone_id = step_id
            step_id += 1

            # Add 2-3 actions per phase
            for action_num in range(1, 4):
                action_step = Step(
                    id=step_id,
                    title=f"Phase {phase} - Action {action_num}",
                    description=f"Specific action for phase {phase}",
                    type=StepType.ACTION,
                    priority=Priority.MEDIUM,
                    status=StepStatus.NOT_STARTED,
                    estimated_duration="3-7 days",
                    resources_needed=[],
                    dependencies=[milestone_id] if action_num == 1 else [step_id - 1],
                    success_criteria=["Define completion criteria"],
                    risks=[],
                    notes="Customize this action based on your specific needs"
                )
                steps.append(action_step)
                step_id += 1

            previous_step_id = milestone_id

        # Phase 1: Initial setup (starting point - closest to present)
        steps.append(Step(
            id=step_id,
            title="Initialize Project",
            description="Set up foundational elements",
            type=StepType.ACTION,
            priority=Priority.CRITICAL,
            status=StepStatus.NOT_STARTED,
            estimated_duration="1-2 days",
            resources_needed=[],
            dependencies=[],
            success_criteria=["Project structure created", "Initial resources gathered"],
            risks=[],
            notes="This is your starting point - what needs to happen first?"
        ))

        # Reverse the list so it goes from present to future
        plan.steps = list(reversed(steps))

        # Fix dependency IDs after reversal
        id_mapping = {step.id: idx for idx, step in enumerate(plan.steps, 1)}
        for idx, step in enumerate(plan.steps, 1):
            step.id = idx
            # Update dependency references
            step.dependencies = [
                id_mapping.get(dep_id, dep_id)
                for dep_id in step.dependencies
            ]

        return plan

    def add_step(self, plan: BackcastPlan, step: Step) -> BackcastPlan:
        """Add a new step to the plan"""
        if not step.id:
            step.id = max([s.id for s in plan.steps], default=0) + 1
        plan.steps.append(step)
        plan.updated_at = datetime.now().isoformat()
        return plan

    def update_step(self, plan: BackcastPlan, step_id: int, **updates) -> BackcastPlan:
        """Update an existing step"""
        for step in plan.steps:
            if step.id == step_id:
                for key, value in updates.items():
                    if hasattr(step, key):
                        setattr(step, key, value)
                step.updated_at = datetime.now().isoformat()
                if updates.get('status') == StepStatus.COMPLETED:
                    step.completed_at = datetime.now().isoformat()
                break
        plan.updated_at = datetime.now().isoformat()
        return plan

    def delete_step(self, plan: BackcastPlan, step_id: int) -> BackcastPlan:
        """Delete a step from the plan"""
        plan.steps = [s for s in plan.steps if s.id != step_id]
        # Remove dependencies pointing to deleted step
        for step in plan.steps:
            step.dependencies = [d for d in step.dependencies if d != step_id]
        plan.updated_at = datetime.now().isoformat()
        return plan

    def get_next_actions(self, plan: BackcastPlan) -> List[Step]:
        """Get steps that are ready to be worked on (no incomplete dependencies)"""
        completed_ids = {s.id for s in plan.steps if s.status == StepStatus.COMPLETED}
        next_actions = []

        for step in plan.steps:
            if step.status in [StepStatus.NOT_STARTED, StepStatus.IN_PROGRESS]:
                # Check if all dependencies are completed
                if all(dep_id in completed_ids for dep_id in step.dependencies):
                    next_actions.append(step)

        # Sort by priority
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3
        }
        next_actions.sort(key=lambda s: priority_order[s.priority])
        return next_actions

    def get_critical_path(self, plan: BackcastPlan) -> List[Step]:
        """Identify the critical path (longest dependency chain)"""
        # Build dependency graph
        step_dict = {s.id: s for s in plan.steps}

        def calculate_path_length(step_id: int, memo: Dict[int, int]) -> int:
            if step_id in memo:
                return memo[step_id]

            step = step_dict.get(step_id)
            if not step or not step.dependencies:
                memo[step_id] = 1
                return 1

            max_dep_length = max(
                calculate_path_length(dep_id, memo)
                for dep_id in step.dependencies
            )
            memo[step_id] = max_dep_length + 1
            return memo[step_id]

        # Calculate path lengths
        memo = {}
        path_lengths = {
            step.id: calculate_path_length(step.id, memo)
            for step in plan.steps
        }

        # Find the longest path
        max_length = max(path_lengths.values(), default=0)
        critical_steps = [
            step for step in plan.steps
            if path_lengths[step.id] == max_length
        ]

        return critical_steps

    def get_blockers(self, plan: BackcastPlan) -> List[Tuple[Step, List[Step]]]:
        """Identify blocked steps and what's blocking them"""
        completed_ids = {s.id for s in plan.steps if s.status == StepStatus.COMPLETED}
        step_dict = {s.id: s for s in plan.steps}
        blockers = []

        for step in plan.steps:
            if step.status == StepStatus.BLOCKED:
                incomplete_deps = [
                    step_dict[dep_id]
                    for dep_id in step.dependencies
                    if dep_id not in completed_ids and dep_id in step_dict
                ]
                if incomplete_deps:
                    blockers.append((step, incomplete_deps))

        return blockers

    def calculate_progress(self, plan: BackcastPlan) -> Dict[str, any]:
        """Calculate overall progress metrics"""
        total = len(plan.steps)
        if total == 0:
            return {"percent": 0, "completed": 0, "total": 0, "in_progress": 0, "blocked": 0}

        completed = sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)
        in_progress = sum(1 for s in plan.steps if s.status == StepStatus.IN_PROGRESS)
        blocked = sum(1 for s in plan.steps if s.status == StepStatus.BLOCKED)

        return {
            "percent": round((completed / total) * 100, 1),
            "completed": completed,
            "total": total,
            "in_progress": in_progress,
            "blocked": blocked,
            "not_started": total - completed - in_progress - blocked
        }

    def save_plan(self, plan: BackcastPlan, filename: str) -> str:
        """Save plan to JSON file"""
        filepath = os.path.join(self.data_dir, filename)

        # Convert to serializable format
        plan_dict = {
            "outcome": asdict(plan.outcome),
            "steps": [self._step_to_dict(s) for s in plan.steps],
            "created_at": plan.created_at,
            "updated_at": plan.updated_at
        }

        with open(filepath, 'w') as f:
            json.dump(plan_dict, f, indent=2)

        return filepath

    def load_plan(self, filename: str) -> BackcastPlan:
        """Load plan from JSON file"""
        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, 'r') as f:
            data = json.load(f)

        outcome = Outcome(**data["outcome"])
        steps = [self._dict_to_step(s) for s in data["steps"]]

        plan = BackcastPlan(
            outcome=outcome,
            steps=steps,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )

        return plan

    def list_plans(self) -> List[str]:
        """List all saved plans"""
        if not os.path.exists(self.data_dir):
            return []
        return [f for f in os.listdir(self.data_dir) if f.endswith('.json')]

    def generate_ai_steps(self, plan: BackcastPlan, num_steps: int = 10) -> BackcastPlan:
        """
        Use AI (OpenAI GPT) to generate intelligent, contextual steps for the plan.
        Falls back to template generation if OpenAI is not available.
        """
        if not HAS_OPENAI:
            print("OpenAI not available, using template generation")
            return self.generate_steps(plan, num_major_phases=5)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY not set, using template generation")
            return self.generate_steps(plan, num_major_phases=5)

        client = openai.OpenAI(api_key=api_key)

        prompt = f"""You are a strategic planning expert. Create a detailed backcasting plan working BACKWARDS from the desired outcome to the present.

OUTCOME:
Title: {plan.outcome.title}
Description: {plan.outcome.description}
Success Criteria: {', '.join(plan.outcome.success_criteria)}
Constraints: {', '.join(plan.outcome.constraints)}
Timeline: {plan.outcome.timeline}

Generate exactly {num_steps} specific, actionable steps. Work backwards from achieving the outcome to what needs to happen first.

Return ONLY a JSON array with this exact structure (no markdown, no explanation):
[
  {{
    "title": "Step title",
    "description": "Detailed description of what needs to be done",
    "type": "action|milestone|decision|dependency|risk_mitigation",
    "priority": "critical|high|medium|low",
    "duration": "estimated time (e.g., '2 weeks', '3 days')",
    "success_criteria": ["criterion 1", "criterion 2"],
    "dependencies": [list of step indices this depends on, 0-indexed],
    "risks": ["potential risk 1", "potential risk 2"]
  }}
]

IMPORTANT:
- Step 0 should be the final outcome achievement
- Last step should be the immediate first action
- Dependencies should only reference steps with LOWER indices (steps that come before)
- Be specific and actionable, not generic"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000
            )

            content = response.choices[0].message.content.strip()
            # Clean up potential markdown formatting
            if content.startswith("```"):
                content = re.sub(r'^```\w*\n?', '', content)
                content = re.sub(r'\n?```$', '', content)

            steps_data = json.loads(content)

            # Convert to Step objects
            plan.steps = []
            for idx, step_data in enumerate(steps_data):
                step = Step(
                    id=idx + 1,
                    title=step_data.get("title", f"Step {idx + 1}"),
                    description=step_data.get("description", ""),
                    type=StepType(step_data.get("type", "action")),
                    priority=Priority(step_data.get("priority", "medium")),
                    status=StepStatus.NOT_STARTED,
                    estimated_duration=step_data.get("duration"),
                    resources_needed=[],
                    dependencies=[d + 1 for d in step_data.get("dependencies", []) if d < idx],
                    success_criteria=step_data.get("success_criteria", []),
                    risks=[
                        Risk(description=r, probability="medium", impact="medium", mitigation="")
                        for r in step_data.get("risks", [])
                    ]
                )
                plan.steps.append(step)

            # Reverse so we go from present to future
            plan.steps = list(reversed(plan.steps))
            # Renumber IDs
            for idx, step in enumerate(plan.steps):
                old_id = step.id
                step.id = idx + 1
                # Update dependencies to new IDs
                step.dependencies = [len(plan.steps) - d + 1 for d in step.dependencies if d <= len(plan.steps)]
                step.dependencies = [d for d in step.dependencies if d < step.id]

            plan.updated_at = datetime.now().isoformat()
            return plan

        except Exception as e:
            print(f"AI generation failed: {e}, using template generation")
            return self.generate_steps(plan, num_major_phases=5)

    def export_to_pdf(self, plan: BackcastPlan, filename: str = None) -> str:
        """Export plan to PDF format"""
        if not HAS_REPORTLAB:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")

        if filename is None:
            safe_title = re.sub(r'[^\w\s-]', '', plan.outcome.title).strip().replace(' ', '_')
            filename = f"{safe_title}.pdf"

        filepath = os.path.join(self.data_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                     fontSize=18, spaceAfter=20, textColor=colors.darkblue)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                       fontSize=14, spaceAfter=10, textColor=colors.darkblue)
        normal_style = styles['Normal']

        story = []

        # Title
        story.append(Paragraph(f"Backcasting Plan: {plan.outcome.title}", title_style))
        story.append(Spacer(1, 12))

        # Outcome section
        story.append(Paragraph("Desired Outcome", heading_style))
        story.append(Paragraph(plan.outcome.description, normal_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Timeline:</b> {plan.outcome.timeline}", normal_style))
        story.append(Spacer(1, 6))

        if plan.outcome.success_criteria:
            story.append(Paragraph("<b>Success Criteria:</b>", normal_style))
            for criterion in plan.outcome.success_criteria:
                story.append(Paragraph(f"  • {criterion}", normal_style))
        story.append(Spacer(1, 12))

        # Progress section
        progress = self.calculate_progress(plan)
        story.append(Paragraph("Progress Overview", heading_style))
        progress_data = [
            ["Metric", "Value"],
            ["Completion", f"{progress['percent']}%"],
            ["Completed Steps", str(progress['completed'])],
            ["In Progress", str(progress['in_progress'])],
            ["Blocked", str(progress['blocked'])],
            ["Not Started", str(progress['not_started'])],
            ["Total Steps", str(progress['total'])]
        ]
        progress_table = Table(progress_data, colWidths=[2*inch, 1.5*inch])
        progress_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(progress_table)
        story.append(Spacer(1, 20))

        # Steps section
        story.append(Paragraph("Action Steps", heading_style))
        for step in plan.steps:
            status_colors = {
                StepStatus.COMPLETED: "green",
                StepStatus.IN_PROGRESS: "blue",
                StepStatus.BLOCKED: "red",
                StepStatus.NOT_STARTED: "gray",
                StepStatus.SKIPPED: "orange"
            }
            color = status_colors.get(step.status, "black")
            story.append(Paragraph(
                f"<b>{step.id}. {step.title}</b> "
                f"<font color='{color}'>[{step.status.value.upper()}]</font> "
                f"<font color='gray'>({step.priority.value})</font>",
                normal_style
            ))
            story.append(Paragraph(f"   {step.description}", normal_style))
            if step.estimated_duration:
                story.append(Paragraph(f"   <i>Duration: {step.estimated_duration}</i>", normal_style))
            story.append(Spacer(1, 8))

        # Build PDF
        doc.build(story)
        return filepath

    def export_to_ical(self, plan: BackcastPlan, filename: str = None, start_date: datetime = None) -> str:
        """Export plan to iCal format for calendar integration"""
        if not HAS_ICALENDAR:
            raise ImportError("icalendar is required for iCal export. Install with: pip install icalendar")

        if filename is None:
            safe_title = re.sub(r'[^\w\s-]', '', plan.outcome.title).strip().replace(' ', '_')
            filename = f"{safe_title}.ics"

        if start_date is None:
            start_date = datetime.now()

        filepath = os.path.join(self.data_dir, filename)

        cal = Calendar()
        cal.add('prodid', '-//Outcome Backcasting Engine//EN')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', f'Backcast: {plan.outcome.title}')

        current_date = start_date

        for step in plan.steps:
            event = Event()
            event.add('summary', f"[{step.priority.value.upper()}] {step.title}")
            event.add('description', f"{step.description}\n\nSuccess Criteria:\n" +
                     "\n".join(f"- {c}" for c in step.success_criteria))

            # Parse duration and calculate dates
            duration_days = self._parse_duration_to_days(step.estimated_duration)
            event.add('dtstart', current_date.date())
            end_date = current_date + timedelta(days=duration_days)
            event.add('dtend', end_date.date())

            # Add status as category
            event.add('categories', [step.status.value, step.type.value])

            # Add priority (iCal uses 1-9, 1 being highest)
            priority_map = {Priority.CRITICAL: 1, Priority.HIGH: 3, Priority.MEDIUM: 5, Priority.LOW: 7}
            event.add('priority', priority_map.get(step.priority, 5))

            cal.add_component(event)
            current_date = end_date

        with open(filepath, 'wb') as f:
            f.write(cal.to_ical())

        return filepath

    def export_to_html(self, plan: BackcastPlan, filename: str = None) -> str:
        """Export plan to a styled HTML report"""
        if filename is None:
            safe_title = re.sub(r'[^\w\s-]', '', plan.outcome.title).strip().replace(' ', '_')
            filename = f"{safe_title}.html"

        filepath = os.path.join(self.data_dir, filename)
        progress = self.calculate_progress(plan)
        next_actions = self.get_next_actions(plan)

        status_colors = {
            "completed": "#10b981",
            "in_progress": "#3b82f6",
            "blocked": "#ef4444",
            "not_started": "#6b7280",
            "skipped": "#f59e0b"
        }

        priority_colors = {
            "critical": "#dc2626",
            "high": "#f97316",
            "medium": "#eab308",
            "low": "#22c55e"
        }

        steps_html = ""
        for step in plan.steps:
            deps = ", ".join(str(d) for d in step.dependencies) if step.dependencies else "None"
            criteria = "".join(f"<li>{c}</li>" for c in step.success_criteria) if step.success_criteria else "<li>Not defined</li>"

            steps_html += f"""
            <div class="step-card" style="border-left: 4px solid {status_colors.get(step.status.value, '#6b7280')}">
                <div class="step-header">
                    <span class="step-id">#{step.id}</span>
                    <span class="step-title">{step.title}</span>
                    <span class="step-status" style="background: {status_colors.get(step.status.value, '#6b7280')}">{step.status.value.replace('_', ' ').title()}</span>
                    <span class="step-priority" style="background: {priority_colors.get(step.priority.value, '#6b7280')}">{step.priority.value.title()}</span>
                </div>
                <p class="step-description">{step.description}</p>
                <div class="step-meta">
                    <span><strong>Type:</strong> {step.type.value.replace('_', ' ').title()}</span>
                    <span><strong>Duration:</strong> {step.estimated_duration or 'Not set'}</span>
                    <span><strong>Dependencies:</strong> {deps}</span>
                </div>
                <div class="step-criteria">
                    <strong>Success Criteria:</strong>
                    <ul>{criteria}</ul>
                </div>
            </div>
            """

        next_actions_html = ""
        for action in next_actions[:5]:
            next_actions_html += f"<li><strong>{action.title}</strong> ({action.priority.value})</li>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backcast Plan: {plan.outcome.title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); min-height: 100vh; color: #e2e8f0; padding: 2rem; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ font-size: 2rem; margin-bottom: 0.5rem; color: #c4b5fd; }}
        h2 {{ font-size: 1.25rem; color: #a5b4fc; margin: 1.5rem 0 1rem; border-bottom: 1px solid #4c1d95; padding-bottom: 0.5rem; }}
        .outcome-box {{ background: rgba(139, 92, 246, 0.2); border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border: 1px solid #7c3aed; }}
        .outcome-box p {{ margin: 0.5rem 0; }}
        .progress-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1rem; margin: 1rem 0; }}
        .progress-card {{ background: rgba(30, 27, 75, 0.8); border-radius: 8px; padding: 1rem; text-align: center; }}
        .progress-card .value {{ font-size: 1.75rem; font-weight: bold; color: #a5b4fc; }}
        .progress-card .label {{ font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; }}
        .progress-bar {{ background: #1e1b4b; border-radius: 999px; height: 12px; overflow: hidden; margin: 1rem 0; }}
        .progress-fill {{ background: linear-gradient(90deg, #7c3aed, #a855f7); height: 100%; border-radius: 999px; transition: width 0.3s; }}
        .step-card {{ background: rgba(30, 27, 75, 0.6); border-radius: 8px; padding: 1rem; margin: 1rem 0; }}
        .step-header {{ display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.75rem; }}
        .step-id {{ background: #4c1d95; color: #e9d5ff; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }}
        .step-title {{ font-weight: 600; flex: 1; color: #e2e8f0; }}
        .step-status, .step-priority {{ padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.7rem; color: white; font-weight: 500; }}
        .step-description {{ color: #cbd5e1; margin-bottom: 0.75rem; line-height: 1.5; }}
        .step-meta {{ display: flex; gap: 1.5rem; font-size: 0.8rem; color: #94a3b8; flex-wrap: wrap; }}
        .step-criteria {{ margin-top: 0.75rem; font-size: 0.85rem; }}
        .step-criteria ul {{ margin-left: 1.5rem; margin-top: 0.25rem; color: #a5b4fc; }}
        .next-actions {{ background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 8px; padding: 1rem; }}
        .next-actions ul {{ margin-left: 1.5rem; }}
        .next-actions li {{ margin: 0.5rem 0; }}
        .footer {{ text-align: center; margin-top: 2rem; color: #64748b; font-size: 0.8rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 {plan.outcome.title}</h1>
        <p style="color: #94a3b8;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

        <div class="outcome-box">
            <p><strong>Description:</strong> {plan.outcome.description}</p>
            <p><strong>Timeline:</strong> {plan.outcome.timeline}</p>
            <p><strong>Success Criteria:</strong> {', '.join(plan.outcome.success_criteria)}</p>
        </div>

        <h2>📊 Progress</h2>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress['percent']}%"></div>
        </div>
        <div class="progress-grid">
            <div class="progress-card"><div class="value">{progress['percent']}%</div><div class="label">Complete</div></div>
            <div class="progress-card"><div class="value">{progress['completed']}</div><div class="label">Done</div></div>
            <div class="progress-card"><div class="value">{progress['in_progress']}</div><div class="label">In Progress</div></div>
            <div class="progress-card"><div class="value">{progress['blocked']}</div><div class="label">Blocked</div></div>
            <div class="progress-card"><div class="value">{progress['not_started']}</div><div class="label">To Do</div></div>
        </div>

        <h2>🎯 Next Actions</h2>
        <div class="next-actions">
            <ul>{next_actions_html if next_actions_html else '<li>No actions ready (check dependencies)</li>'}</ul>
        </div>

        <h2>📝 All Steps ({len(plan.steps)} total)</h2>
        {steps_html}

        <div class="footer">
            <p>Generated by Outcome Backcasting Engine</p>
        </div>
    </div>
</body>
</html>"""

        with open(filepath, 'w') as f:
            f.write(html)

        return filepath

    def _parse_duration_to_days(self, duration: str) -> int:
        """Parse duration string to number of days"""
        if not duration:
            return 7  # Default 1 week

        duration = duration.lower()
        # Try to extract number
        match = re.search(r'(\d+)', duration)
        if not match:
            return 7

        num = int(match.group(1))

        if 'day' in duration:
            return num
        elif 'week' in duration:
            return num * 7
        elif 'month' in duration:
            return num * 30
        elif 'hour' in duration:
            return max(1, num // 8)  # Convert hours to work days
        else:
            return num  # Assume days

    def _step_to_dict(self, step: Step) -> Dict:
        """Convert Step to dictionary for JSON serialization"""
        step_dict = asdict(step)
        step_dict['type'] = step.type.value
        step_dict['priority'] = step.priority.value
        step_dict['status'] = step.status.value
        return step_dict

    def _dict_to_step(self, data: Dict) -> Step:
        """Convert dictionary to Step object"""
        # Convert enum strings back to enums
        data['type'] = StepType(data['type'])
        data['priority'] = Priority(data['priority'])
        data['status'] = StepStatus(data['status'])

        # Convert nested Resource dicts
        data['resources_needed'] = [
            Resource(**r) if isinstance(r, dict) else r
            for r in data.get('resources_needed', [])
        ]

        # Convert nested Risk dicts
        data['risks'] = [
            Risk(**r) if isinstance(r, dict) else r
            for r in data.get('risks', [])
        ]

        return Step(**data)


class BackcastAnalyzer:
    """Analyzes backcasting plans for insights and recommendations"""

    @staticmethod
    def analyze_risks(plan: BackcastPlan) -> Dict[str, List]:
        """Analyze all risks in the plan"""
        high_risk_steps = []
        all_risks = []

        for step in plan.steps:
            for risk in step.risks:
                risk_info = {
                    "step": step.title,
                    "step_id": step.id,
                    "risk": risk.description,
                    "probability": risk.probability,
                    "impact": risk.impact,
                    "mitigation": risk.mitigation
                }
                all_risks.append(risk_info)

                if risk.probability in ["high", "medium"] and risk.impact in ["high", "medium"]:
                    high_risk_steps.append(risk_info)

        return {
            "high_priority_risks": high_risk_steps,
            "all_risks": all_risks,
            "risk_count": len(all_risks)
        }

    @staticmethod
    def analyze_resources(plan: BackcastPlan) -> Dict[str, any]:
        """Analyze resource requirements"""
        resource_summary = {}

        for step in plan.steps:
            for resource in step.resources_needed:
                if resource.type not in resource_summary:
                    resource_summary[resource.type] = []
                resource_summary[resource.type].append({
                    "step": step.title,
                    "resource": resource.name,
                    "amount": resource.amount,
                    "notes": resource.notes
                })

        return resource_summary

    @staticmethod
    def suggest_optimizations(plan: BackcastPlan) -> List[str]:
        """Suggest potential optimizations to the plan"""
        suggestions = []

        # Check for steps with no dependencies that could be parallelized
        no_dep_steps = [s for s in plan.steps if not s.dependencies]
        if len(no_dep_steps) > 3:
            suggestions.append(
                f"Found {len(no_dep_steps)} independent steps that could potentially be "
                "parallelized or reordered for efficiency."
            )

        # Check for bottlenecks (steps with many dependents)
        step_dependents = {}
        for step in plan.steps:
            for dep_id in step.dependencies:
                step_dependents[dep_id] = step_dependents.get(dep_id, 0) + 1

        bottlenecks = [
            (step_id, count) for step_id, count in step_dependents.items()
            if count >= 3
        ]
        if bottlenecks:
            suggestions.append(
                f"Found {len(bottlenecks)} potential bottleneck steps that many other "
                "steps depend on. Consider breaking these down or starting them early."
            )

        # Check for steps without success criteria
        no_criteria = [s for s in plan.steps if not s.success_criteria or
                      s.success_criteria == ["Define specific criteria"]]
        if no_criteria:
            suggestions.append(
                f"{len(no_criteria)} steps lack specific success criteria. "
                "Define clear completion criteria for better tracking."
            )

        # Check for high-risk steps without mitigation
        high_risk_no_mitigation = []
        for step in plan.steps:
            for risk in step.risks:
                if (risk.probability == "high" or risk.impact == "high") and \
                   not risk.mitigation:
                    high_risk_no_mitigation.append(step.title)

        if high_risk_no_mitigation:
            suggestions.append(
                f"{len(high_risk_no_mitigation)} high-risk items lack mitigation strategies."
            )

        if not suggestions:
            suggestions.append("Plan looks well-structured! No major optimization suggestions.")

        return suggestions
