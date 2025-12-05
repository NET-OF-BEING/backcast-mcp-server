#!/usr/bin/env python3
"""
Interactive CLI for Outcome Backcasting Engine
"""

import os
import sys
from typing import Optional
from backcast_engine import (
    BackcastEngine, BackcastAnalyzer, BackcastPlan,
    Outcome, Step, Resource, Risk,
    StepType, StepStatus, Priority
)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class BackcastCLI:
    """Interactive command-line interface"""

    def __init__(self):
        self.engine = BackcastEngine()
        self.analyzer = BackcastAnalyzer()
        self.current_plan: Optional[BackcastPlan] = None
        self.current_filename: Optional[str] = None

    def print_header(self, text: str):
        """Print colored header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")

    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

    def input_multiline(self, prompt: str) -> str:
        """Get multiline input from user"""
        print(f"{prompt} (press Ctrl+D or type 'END' on a new line when done):")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
        except EOFError:
            pass
        return '\n'.join(lines)

    def input_list(self, prompt: str) -> list:
        """Get a list of items from user"""
        print(f"{prompt} (one per line, press Ctrl+D or type 'END' when done):")
        items = []
        try:
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                if line.strip():
                    items.append(line.strip())
        except EOFError:
            pass
        return items

    def create_new_plan(self):
        """Wizard to create a new backcasting plan"""
        self.print_header("Create New Backcasting Plan")

        print(f"{Colors.BOLD}Let's define your desired outcome:{Colors.ENDC}\n")

        title = input("Outcome title: ").strip()
        if not title:
            self.print_error("Title is required!")
            return

        description = self.input_multiline("Outcome description")
        if not description:
            self.print_error("Description is required!")
            return

        print("\n" + f"{Colors.BOLD}Define success criteria (what does 'done' look like?):{Colors.ENDC}")
        success_criteria = self.input_list("Success criteria")

        print("\n" + f"{Colors.BOLD}Define constraints (limitations, requirements, non-negotiables):{Colors.ENDC}")
        constraints = self.input_list("Constraints")

        timeline = input("\nTimeline (e.g., '6 months', '1 year'): ").strip()

        # Create outcome
        outcome = Outcome(
            title=title,
            description=description,
            success_criteria=success_criteria if success_criteria else ["Define criteria"],
            constraints=constraints if constraints else [],
            timeline=timeline if timeline else "To be determined"
        )

        # Create plan
        self.current_plan = self.engine.create_plan(outcome)

        # Ask if user wants auto-generated template
        print(f"\n{Colors.CYAN}Would you like to generate a template structure? (y/n):{Colors.ENDC} ", end="")
        if input().lower() == 'y':
            num_phases = input("How many major phases? (default 5): ").strip()
            num_phases = int(num_phases) if num_phases.isdigit() else 5
            self.current_plan = self.engine.generate_steps(self.current_plan, num_phases)
            self.print_success(f"Generated {len(self.current_plan.steps)} template steps")

        self.print_success("Plan created successfully!")

        # Save the plan
        default_name = title.lower().replace(' ', '_')[:30] + '.json'
        filename = input(f"\nSave as (default: {default_name}): ").strip()
        filename = filename if filename else default_name
        if not filename.endswith('.json'):
            filename += '.json'

        self.current_filename = filename
        filepath = self.engine.save_plan(self.current_plan, filename)
        self.print_success(f"Plan saved to {filepath}")

    def load_plan(self):
        """Load an existing plan"""
        plans = self.engine.list_plans()

        if not plans:
            self.print_warning("No saved plans found.")
            return

        self.print_header("Load Existing Plan")
        print("Available plans:\n")
        for idx, plan_name in enumerate(plans, 1):
            print(f"  {idx}. {plan_name}")

        choice = input(f"\nEnter number (1-{len(plans)}) or filename: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(plans):
            filename = plans[int(choice) - 1]
        else:
            filename = choice if choice.endswith('.json') else choice + '.json'

        try:
            self.current_plan = self.engine.load_plan(filename)
            self.current_filename = filename
            self.print_success(f"Loaded plan: {self.current_plan.outcome.title}")
        except FileNotFoundError:
            self.print_error(f"Plan '{filename}' not found!")
        except Exception as e:
            self.print_error(f"Error loading plan: {e}")

    def view_plan_overview(self):
        """Display plan overview"""
        if not self.current_plan:
            self.print_warning("No plan loaded. Create or load a plan first.")
            return

        self.print_header(f"Plan Overview: {self.current_plan.outcome.title}")

        # Outcome details
        print(f"{Colors.BOLD}Outcome:{Colors.ENDC}")
        print(f"  {self.current_plan.outcome.description}\n")
        print(f"{Colors.BOLD}Timeline:{Colors.ENDC} {self.current_plan.outcome.timeline}\n")

        # Success criteria
        print(f"{Colors.BOLD}Success Criteria:{Colors.ENDC}")
        for criterion in self.current_plan.outcome.success_criteria:
            print(f"  • {criterion}")

        # Constraints
        if self.current_plan.outcome.constraints:
            print(f"\n{Colors.BOLD}Constraints:{Colors.ENDC}")
            for constraint in self.current_plan.outcome.constraints:
                print(f"  • {constraint}")

        # Progress
        progress = self.engine.calculate_progress(self.current_plan)
        print(f"\n{Colors.BOLD}Progress:{Colors.ENDC}")
        print(f"  {progress['percent']}% Complete ({progress['completed']}/{progress['total']} steps)")
        print(f"  In Progress: {progress['in_progress']}")
        print(f"  Blocked: {progress['blocked']}")
        print(f"  Not Started: {progress['not_started']}")

    def view_all_steps(self):
        """Display all steps"""
        if not self.current_plan:
            self.print_warning("No plan loaded.")
            return

        self.print_header("All Steps")

        for step in self.current_plan.steps:
            self._display_step_summary(step)

    def view_step_details(self):
        """Display detailed view of a specific step"""
        if not self.current_plan:
            self.print_warning("No plan loaded.")
            return

        step_id = input("Enter step ID: ").strip()
        if not step_id.isdigit():
            self.print_error("Invalid step ID!")
            return

        step = next((s for s in self.current_plan.steps if s.id == int(step_id)), None)
        if not step:
            self.print_error(f"Step {step_id} not found!")
            return

        self._display_step_details(step)

    def _display_step_summary(self, step: Step):
        """Display a summary of a step"""
        status_colors = {
            StepStatus.COMPLETED: Colors.GREEN,
            StepStatus.IN_PROGRESS: Colors.YELLOW,
            StepStatus.BLOCKED: Colors.RED,
            StepStatus.NOT_STARTED: Colors.CYAN,
            StepStatus.SKIPPED: Colors.CYAN
        }

        priority_symbols = {
            Priority.CRITICAL: "🔴",
            Priority.HIGH: "🟠",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "⚪"
        }

        type_symbols = {
            StepType.MILESTONE: "🎯",
            StepType.ACTION: "⚡",
            StepType.DECISION: "🤔",
            StepType.DEPENDENCY: "🔗",
            StepType.RISK_MITIGATION: "🛡️"
        }

        color = status_colors.get(step.status, Colors.ENDC)
        priority = priority_symbols.get(step.priority, "")
        type_symbol = type_symbols.get(step.type, "")

        print(f"{color}[{step.id:2d}] {priority} {type_symbol} {step.title}{Colors.ENDC}")
        print(f"     Status: {step.status.value.replace('_', ' ').title()} | "
              f"Priority: {step.priority.value.title()} | "
              f"Type: {step.type.value.replace('_', ' ').title()}")
        if step.dependencies:
            print(f"     Dependencies: {', '.join(map(str, step.dependencies))}")
        print()

    def _display_step_details(self, step: Step):
        """Display full details of a step"""
        self.print_header(f"Step {step.id}: {step.title}")

        print(f"{Colors.BOLD}Description:{Colors.ENDC}")
        print(f"  {step.description}\n")

        print(f"{Colors.BOLD}Status:{Colors.ENDC} {step.status.value.replace('_', ' ').title()}")
        print(f"{Colors.BOLD}Priority:{Colors.ENDC} {step.priority.value.title()}")
        print(f"{Colors.BOLD}Type:{Colors.ENDC} {step.type.value.replace('_', ' ').title()}")

        if step.estimated_duration:
            print(f"{Colors.BOLD}Estimated Duration:{Colors.ENDC} {step.estimated_duration}")

        if step.dependencies:
            print(f"\n{Colors.BOLD}Dependencies (must complete first):{Colors.ENDC}")
            for dep_id in step.dependencies:
                dep_step = next((s for s in self.current_plan.steps if s.id == dep_id), None)
                if dep_step:
                    status_icon = "✓" if dep_step.status == StepStatus.COMPLETED else "○"
                    print(f"  {status_icon} [{dep_id}] {dep_step.title}")

        if step.success_criteria:
            print(f"\n{Colors.BOLD}Success Criteria:{Colors.ENDC}")
            for criterion in step.success_criteria:
                print(f"  • {criterion}")

        if step.resources_needed:
            print(f"\n{Colors.BOLD}Resources Needed:{Colors.ENDC}")
            for resource in step.resources_needed:
                amount_str = f" ({resource.amount})" if resource.amount else ""
                print(f"  • {resource.name} ({resource.type}){amount_str}")
                if resource.notes:
                    print(f"    Note: {resource.notes}")

        if step.risks:
            print(f"\n{Colors.BOLD}Risks:{Colors.ENDC}")
            for risk in step.risks:
                print(f"  • {risk.description}")
                print(f"    Probability: {risk.probability} | Impact: {risk.impact}")
                if risk.mitigation:
                    print(f"    Mitigation: {risk.mitigation}")

        if step.notes:
            print(f"\n{Colors.BOLD}Notes:{Colors.ENDC}")
            print(f"  {step.notes}")

        print(f"\n{Colors.BOLD}Timestamps:{Colors.ENDC}")
        print(f"  Created: {step.created_at}")
        print(f"  Updated: {step.updated_at}")
        if step.completed_at:
            print(f"  Completed: {step.completed_at}")

    def view_next_actions(self):
        """Display next actionable steps"""
        if not self.current_plan:
            self.print_warning("No plan loaded.")
            return

        next_actions = self.engine.get_next_actions(self.current_plan)

        self.print_header("Next Actions (Ready to Start)")

        if not next_actions:
            self.print_info("No available actions! Either all steps are complete or blocked.")
            return

        for step in next_actions:
            self._display_step_summary(step)

    def view_critical_path(self):
        """Display critical path analysis"""
        if not self.current_plan:
            self.print_warning("No plan loaded.")
            return

        critical_steps = self.engine.get_critical_path(self.current_plan)

        self.print_header("Critical Path (Longest Dependency Chain)")

        if not critical_steps:
            self.print_info("No critical path identified.")
            return

        self.print_info(f"Found {len(critical_steps)} steps on the critical path:\n")

        for step in critical_steps:
            self._display_step_summary(step)

    def update_step_status(self):
        """Update the status of a step"""
        if not self.current_plan:
            self.print_warning("No plan loaded.")
            return

        step_id = input("Enter step ID: ").strip()
        if not step_id.isdigit():
            self.print_error("Invalid step ID!")
            return

        step_id = int(step_id)
        step = next((s for s in self.current_plan.steps if s.id == step_id), None)
        if not step:
            self.print_error(f"Step {step_id} not found!")
            return

        print(f"\nCurrent status: {step.status.value}\n")
        print("New status:")
        print("  1. Not Started")
        print("  2. In Progress")
        print("  3. Completed")
        print("  4. Blocked")
        print("  5. Skipped")

        choice = input("\nEnter choice (1-5): ").strip()
        status_map = {
            '1': StepStatus.NOT_STARTED,
            '2': StepStatus.IN_PROGRESS,
            '3': StepStatus.COMPLETED,
            '4': StepStatus.BLOCKED,
            '5': StepStatus.SKIPPED
        }

        if choice in status_map:
            self.current_plan = self.engine.update_step(
                self.current_plan,
                step_id,
                status=status_map[choice]
            )
            self._save_current_plan()
            self.print_success(f"Step {step_id} status updated to {status_map[choice].value}")
        else:
            self.print_error("Invalid choice!")

    def add_new_step(self):
        """Add a new step to the plan"""
        if not self.current_plan:
            self.print_warning("No plan loaded.")
            return

        self.print_header("Add New Step")

        title = input("Step title: ").strip()
        if not title:
            self.print_error("Title is required!")
            return

        description = self.input_multiline("Step description")

        print("\nStep type:")
        print("  1. Action")
        print("  2. Milestone")
        print("  3. Decision")
        print("  4. Dependency")
        print("  5. Risk Mitigation")
        type_choice = input("Enter choice (1-5, default 1): ").strip()
        type_map = {
            '1': StepType.ACTION, '2': StepType.MILESTONE, '3': StepType.DECISION,
            '4': StepType.DEPENDENCY, '5': StepType.RISK_MITIGATION
        }
        step_type = type_map.get(type_choice, StepType.ACTION)

        print("\nPriority:")
        print("  1. Critical")
        print("  2. High")
        print("  3. Medium")
        print("  4. Low")
        priority_choice = input("Enter choice (1-4, default 3): ").strip()
        priority_map = {
            '1': Priority.CRITICAL, '2': Priority.HIGH,
            '3': Priority.MEDIUM, '4': Priority.LOW
        }
        priority = priority_map.get(priority_choice, Priority.MEDIUM)

        estimated_duration = input("\nEstimated duration (e.g., '3 days', '2 weeks'): ").strip()

        print("\nDependencies (step IDs that must be completed first):")
        dep_input = input("Enter comma-separated IDs (e.g., 1,3,5) or leave blank: ").strip()
        dependencies = []
        if dep_input:
            dependencies = [int(x.strip()) for x in dep_input.split(',') if x.strip().isdigit()]

        print("\n" + f"{Colors.BOLD}Success criteria:{Colors.ENDC}")
        success_criteria = self.input_list("Criteria")

        # Create new step
        new_step = Step(
            id=0,  # Will be assigned by engine
            title=title,
            description=description,
            type=step_type,
            priority=priority,
            status=StepStatus.NOT_STARTED,
            estimated_duration=estimated_duration if estimated_duration else None,
            resources_needed=[],
            dependencies=dependencies,
            success_criteria=success_criteria if success_criteria else ["Define criteria"],
            risks=[]
        )

        self.current_plan = self.engine.add_step(self.current_plan, new_step)
        self._save_current_plan()
        self.print_success(f"Added step {new_step.id}: {title}")

    def delete_step(self):
        """Delete a step from the plan"""
        if not self.current_plan:
            self.print_warning("No plan loaded.")
            return

        step_id = input("Enter step ID to delete: ").strip()
        if not step_id.isdigit():
            self.print_error("Invalid step ID!")
            return

        step_id = int(step_id)
        step = next((s for s in self.current_plan.steps if s.id == step_id), None)
        if not step:
            self.print_error(f"Step {step_id} not found!")
            return

        confirm = input(f"Delete step '{step.title}'? (y/n): ").lower()
        if confirm == 'y':
            self.current_plan = self.engine.delete_step(self.current_plan, step_id)
            self._save_current_plan()
            self.print_success(f"Step {step_id} deleted")

    def analyze_plan(self):
        """Run analysis on the current plan"""
        if not self.current_plan:
            self.print_warning("No plan loaded.")
            return

        self.print_header("Plan Analysis")

        # Progress
        progress = self.engine.calculate_progress(self.current_plan)
        print(f"{Colors.BOLD}Progress Summary:{Colors.ENDC}")
        print(f"  {progress['percent']}% Complete")
        print(f"  {progress['completed']} completed, {progress['in_progress']} in progress")
        print(f"  {progress['blocked']} blocked, {progress['not_started']} not started\n")

        # Risks
        risk_analysis = self.analyzer.analyze_risks(self.current_plan)
        print(f"{Colors.BOLD}Risk Analysis:{Colors.ENDC}")
        print(f"  Total risks identified: {risk_analysis['risk_count']}")
        print(f"  High-priority risks: {len(risk_analysis['high_priority_risks'])}")

        if risk_analysis['high_priority_risks']:
            print(f"\n  {Colors.RED}High-Priority Risks:{Colors.ENDC}")
            for risk in risk_analysis['high_priority_risks'][:5]:
                print(f"    • {risk['step']}: {risk['risk']}")

        # Resources
        print(f"\n{Colors.BOLD}Resource Requirements:{Colors.ENDC}")
        resources = self.analyzer.analyze_resources(self.current_plan)
        if resources:
            for resource_type, items in resources.items():
                print(f"  {resource_type.title()}: {len(items)} items")
        else:
            print("  No resources defined yet")

        # Optimizations
        print(f"\n{Colors.BOLD}Optimization Suggestions:{Colors.ENDC}")
        suggestions = self.analyzer.suggest_optimizations(self.current_plan)
        for idx, suggestion in enumerate(suggestions, 1):
            print(f"  {idx}. {suggestion}")

        # Blockers
        blockers = self.engine.get_blockers(self.current_plan)
        if blockers:
            print(f"\n{Colors.BOLD}{Colors.RED}Current Blockers:{Colors.ENDC}")
            for blocked_step, blocking_steps in blockers:
                print(f"  • {blocked_step.title} is blocked by:")
                for blocking in blocking_steps:
                    print(f"    - [{blocking.id}] {blocking.title}")

    def export_plan(self):
        """Export plan to different formats"""
        if not self.current_plan:
            self.print_warning("No plan loaded.")
            return

        print("\nExport format:")
        print("  1. Markdown (.md)")
        print("  2. Text (.txt)")
        print("  3. CSV (.csv)")

        choice = input("Enter choice (1-3): ").strip()

        if choice == '1':
            self._export_markdown()
        elif choice == '2':
            self._export_text()
        elif choice == '3':
            self._export_csv()
        else:
            self.print_error("Invalid choice!")

    def _export_markdown(self):
        """Export to markdown format"""
        filename = input("Filename (without extension): ").strip()
        if not filename:
            filename = "backcast_plan"

        filepath = os.path.join(self.engine.data_dir, filename + '.md')

        with open(filepath, 'w') as f:
            f.write(f"# {self.current_plan.outcome.title}\n\n")
            f.write(f"**Timeline:** {self.current_plan.outcome.timeline}\n\n")
            f.write(f"## Outcome Description\n\n")
            f.write(f"{self.current_plan.outcome.description}\n\n")

            f.write(f"## Success Criteria\n\n")
            for criterion in self.current_plan.outcome.success_criteria:
                f.write(f"- {criterion}\n")

            if self.current_plan.outcome.constraints:
                f.write(f"\n## Constraints\n\n")
                for constraint in self.current_plan.outcome.constraints:
                    f.write(f"- {constraint}\n")

            progress = self.engine.calculate_progress(self.current_plan)
            f.write(f"\n## Progress: {progress['percent']}%\n\n")
            f.write(f"- Completed: {progress['completed']}\n")
            f.write(f"- In Progress: {progress['in_progress']}\n")
            f.write(f"- Not Started: {progress['not_started']}\n")
            f.write(f"- Blocked: {progress['blocked']}\n")

            f.write(f"\n## Steps\n\n")
            for step in self.current_plan.steps:
                status_icon = {
                    StepStatus.COMPLETED: "✅",
                    StepStatus.IN_PROGRESS: "🔄",
                    StepStatus.BLOCKED: "🚫",
                    StepStatus.NOT_STARTED: "⭕",
                    StepStatus.SKIPPED: "⏭️"
                }.get(step.status, "⭕")

                f.write(f"### {status_icon} [{step.id}] {step.title}\n\n")
                f.write(f"**Status:** {step.status.value.title()} | ")
                f.write(f"**Priority:** {step.priority.value.title()} | ")
                f.write(f"**Type:** {step.type.value.replace('_', ' ').title()}\n\n")

                f.write(f"{step.description}\n\n")

                if step.dependencies:
                    f.write(f"**Dependencies:** {', '.join(map(str, step.dependencies))}\n\n")

                if step.estimated_duration:
                    f.write(f"**Duration:** {step.estimated_duration}\n\n")

                if step.success_criteria and step.success_criteria != ["Define specific criteria"]:
                    f.write(f"**Success Criteria:**\n")
                    for criterion in step.success_criteria:
                        f.write(f"- {criterion}\n")
                    f.write("\n")

                if step.resources_needed:
                    f.write(f"**Resources:**\n")
                    for resource in step.resources_needed:
                        f.write(f"- {resource.name} ({resource.type})\n")
                    f.write("\n")

                if step.risks:
                    f.write(f"**Risks:**\n")
                    for risk in step.risks:
                        f.write(f"- {risk.description} (P:{risk.probability}, I:{risk.impact})\n")
                        if risk.mitigation:
                            f.write(f"  - Mitigation: {risk.mitigation}\n")
                    f.write("\n")

                f.write("---\n\n")

        self.print_success(f"Exported to {filepath}")

    def _export_text(self):
        """Export to plain text format"""
        filename = input("Filename (without extension): ").strip()
        if not filename:
            filename = "backcast_plan"

        filepath = os.path.join(self.engine.data_dir, filename + '.txt')

        with open(filepath, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write(f"{self.current_plan.outcome.title}\n".center(70))
            f.write("=" * 70 + "\n\n")

            f.write(f"Timeline: {self.current_plan.outcome.timeline}\n\n")
            f.write(f"Description:\n{self.current_plan.outcome.description}\n\n")

            progress = self.engine.calculate_progress(self.current_plan)
            f.write(f"Progress: {progress['percent']}% ({progress['completed']}/{progress['total']} steps)\n\n")

            f.write("STEPS:\n")
            f.write("-" * 70 + "\n")

            for step in self.current_plan.steps:
                f.write(f"\n[{step.id:2d}] {step.title}\n")
                f.write(f"     Status: {step.status.value} | Priority: {step.priority.value}\n")
                f.write(f"     {step.description}\n")

                if step.dependencies:
                    f.write(f"     Dependencies: {', '.join(map(str, step.dependencies))}\n")

                f.write("\n")

        self.print_success(f"Exported to {filepath}")

    def _export_csv(self):
        """Export to CSV format"""
        import csv

        filename = input("Filename (without extension): ").strip()
        if not filename:
            filename = "backcast_plan"

        filepath = os.path.join(self.engine.data_dir, filename + '.csv')

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Title', 'Description', 'Type', 'Status', 'Priority',
                'Duration', 'Dependencies', 'Success Criteria'
            ])

            for step in self.current_plan.steps:
                writer.writerow([
                    step.id,
                    step.title,
                    step.description,
                    step.type.value,
                    step.status.value,
                    step.priority.value,
                    step.estimated_duration or '',
                    '; '.join(map(str, step.dependencies)),
                    '; '.join(step.success_criteria)
                ])

        self.print_success(f"Exported to {filepath}")

    def _save_current_plan(self):
        """Save the current plan"""
        if self.current_plan and self.current_filename:
            self.engine.save_plan(self.current_plan, self.current_filename)

    def show_menu(self):
        """Display main menu"""
        print(f"\n{Colors.CYAN}{'─'*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}Outcome Backcasting Engine{Colors.ENDC}")
        if self.current_plan:
            print(f"Current: {Colors.GREEN}{self.current_plan.outcome.title}{Colors.ENDC}")
        print(f"{Colors.CYAN}{'─'*70}{Colors.ENDC}")

        print("\n" + f"{Colors.BOLD}Plan Management:{Colors.ENDC}")
        print("  1. Create new plan")
        print("  2. Load existing plan")
        print("  3. View plan overview")

        print("\n" + f"{Colors.BOLD}View Steps:{Colors.ENDC}")
        print("  4. View all steps")
        print("  5. View step details")
        print("  6. View next actions")
        print("  7. View critical path")

        print("\n" + f"{Colors.BOLD}Edit Plan:{Colors.ENDC}")
        print("  8. Add new step")
        print("  9. Update step status")
        print(" 10. Delete step")

        print("\n" + f"{Colors.BOLD}Analysis:{Colors.ENDC}")
        print(" 11. Analyze plan")
        print(" 12. Export plan")

        print("\n" + f"{Colors.BOLD}Other:{Colors.ENDC}")
        print("  0. Exit")

        print(f"\n{Colors.CYAN}{'─'*70}{Colors.ENDC}")

    def run(self):
        """Main CLI loop"""
        self.print_header("Welcome to Outcome Backcasting Engine")
        self.print_info("Reverse-engineer your path to success!\n")

        while True:
            self.show_menu()
            choice = input(f"\n{Colors.BOLD}Enter choice:{Colors.ENDC} ").strip()

            if choice == '0':
                print(f"\n{Colors.GREEN}Thanks for using Outcome Backcasting Engine!{Colors.ENDC}\n")
                break
            elif choice == '1':
                self.create_new_plan()
            elif choice == '2':
                self.load_plan()
            elif choice == '3':
                self.view_plan_overview()
            elif choice == '4':
                self.view_all_steps()
            elif choice == '5':
                self.view_step_details()
            elif choice == '6':
                self.view_next_actions()
            elif choice == '7':
                self.view_critical_path()
            elif choice == '8':
                self.add_new_step()
            elif choice == '9':
                self.update_step_status()
            elif choice == '10':
                self.delete_step()
            elif choice == '11':
                self.analyze_plan()
            elif choice == '12':
                self.export_plan()
            else:
                self.print_error("Invalid choice!")

            if choice != '0':
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


if __name__ == '__main__':
    cli = BackcastCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user. Goodbye!{Colors.ENDC}\n")
        sys.exit(0)
