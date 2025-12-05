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
