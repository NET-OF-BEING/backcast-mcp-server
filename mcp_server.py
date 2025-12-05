#!/usr/bin/env python3
"""
MCP Server for Outcome Backcasting Engine

Allows AI assistants (Claude Code, ChatGPT, etc.) to use backcasting
via the Model Context Protocol (MCP).

This turns the backcasting engine into an AI tool that can be called
programmatically by AI assistants.
"""

import json
import sys
from typing import List, Dict, Any, Optional
from backcast_engine import (
    BackcastEngine, BackcastAnalyzer,
    Outcome, Step, Resource, Risk,
    StepType, StepStatus, Priority
)


class BackcastMCPServer:
    """MCP Server exposing backcasting functionality to AI tools"""

    def __init__(self):
        self.engine = BackcastEngine()
        self.analyzer = BackcastAnalyzer()
        self.current_plan = None

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        params = request.get("params", {})

        try:
            if method == "tools/list":
                return self._list_tools()
            elif method == "tools/call":
                return self._call_tool(params)
            else:
                return self._error(f"Unknown method: {method}")
        except Exception as e:
            return self._error(str(e))

    def _list_tools(self) -> Dict[str, Any]:
        """Return list of available tools"""
        return {
            "tools": [
                {
                    "name": "backcast_create_plan",
                    "description": "Create a new backcasting plan from an outcome description",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Outcome title"},
                            "description": {"type": "string", "description": "Detailed outcome description"},
                            "success_criteria": {"type": "array", "items": {"type": "string"}},
                            "constraints": {"type": "array", "items": {"type": "string"}},
                            "timeline": {"type": "string", "description": "Timeline (e.g., '6 months')"},
                            "num_phases": {"type": "integer", "default": 5, "description": "Number of major phases"}
                        },
                        "required": ["title", "description"]
                    }
                },
                {
                    "name": "backcast_load_plan",
                    "description": "Load an existing plan by filename",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Plan filename (with .json)"}
                        },
                        "required": ["filename"]
                    }
                },
                {
                    "name": "backcast_list_plans",
                    "description": "List all saved plans",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "backcast_get_overview",
                    "description": "Get overview of current plan (outcome, progress, summary)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "backcast_get_all_steps",
                    "description": "Get all steps in the current plan",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "include_details": {"type": "boolean", "default": False}
                        }
                    }
                },
                {
                    "name": "backcast_get_next_actions",
                    "description": "Get steps that are ready to work on (dependencies met)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "backcast_get_critical_path",
                    "description": "Get critical path (longest dependency chain)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "backcast_add_step",
                    "description": "Add a new step to the current plan",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "type": {"type": "string", "enum": ["milestone", "action", "decision", "dependency", "risk_mitigation"]},
                            "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                            "duration": {"type": "string"},
                            "dependencies": {"type": "array", "items": {"type": "integer"}},
                            "success_criteria": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["title", "description"]
                    }
                },
                {
                    "name": "backcast_update_step_status",
                    "description": "Update the status of a step",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "step_id": {"type": "integer"},
                            "status": {"type": "string", "enum": ["not_started", "in_progress", "completed", "blocked", "skipped"]}
                        },
                        "required": ["step_id", "status"]
                    }
                },
                {
                    "name": "backcast_analyze_plan",
                    "description": "Get comprehensive analysis (progress, risks, resources, suggestions)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "backcast_save_plan",
                    "description": "Save current plan to file",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string"}
                        },
                        "required": ["filename"]
                    }
                },
                {
                    "name": "backcast_export_markdown",
                    "description": "Export current plan to Markdown format",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string"}
                        },
                        "required": ["filename"]
                    }
                }
            ]
        }

    def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        # Route to appropriate handler
        handlers = {
            "backcast_create_plan": self._create_plan,
            "backcast_load_plan": self._load_plan,
            "backcast_list_plans": self._list_plans,
            "backcast_get_overview": self._get_overview,
            "backcast_get_all_steps": self._get_all_steps,
            "backcast_get_next_actions": self._get_next_actions,
            "backcast_get_critical_path": self._get_critical_path,
            "backcast_add_step": self._add_step,
            "backcast_update_step_status": self._update_step_status,
            "backcast_analyze_plan": self._analyze_plan,
            "backcast_save_plan": self._save_plan,
            "backcast_export_markdown": self._export_markdown
        }

        handler = handlers.get(tool_name)
        if not handler:
            return self._error(f"Unknown tool: {tool_name}")

        result = handler(arguments)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    def _create_plan(self, args: Dict) -> Dict:
        """Create a new plan"""
        outcome = Outcome(
            title=args["title"],
            description=args["description"],
            success_criteria=args.get("success_criteria", []),
            constraints=args.get("constraints", []),
            timeline=args.get("timeline", "To be determined")
        )

        self.current_plan = self.engine.create_plan(outcome)

        # Generate template if requested
        num_phases = args.get("num_phases", 5)
        if num_phases > 0:
            self.current_plan = self.engine.generate_steps(self.current_plan, num_phases)

        return {
            "status": "success",
            "message": f"Plan created: {outcome.title}",
            "steps_generated": len(self.current_plan.steps)
        }

    def _load_plan(self, args: Dict) -> Dict:
        """Load an existing plan"""
        filename = args["filename"]
        self.current_plan = self.engine.load_plan(filename)
        return {
            "status": "success",
            "message": f"Plan loaded: {self.current_plan.outcome.title}",
            "steps": len(self.current_plan.steps)
        }

    def _list_plans(self, args: Dict) -> Dict:
        """List all plans"""
        plans = self.engine.list_plans()
        return {
            "status": "success",
            "plans": plans,
            "count": len(plans)
        }

    def _get_overview(self, args: Dict) -> Dict:
        """Get plan overview"""
        if not self.current_plan:
            return {"status": "error", "message": "No plan loaded"}

        progress = self.engine.calculate_progress(self.current_plan)

        return {
            "status": "success",
            "outcome": {
                "title": self.current_plan.outcome.title,
                "description": self.current_plan.outcome.description,
                "timeline": self.current_plan.outcome.timeline,
                "success_criteria": self.current_plan.outcome.success_criteria,
                "constraints": self.current_plan.outcome.constraints
            },
            "progress": progress,
            "total_steps": len(self.current_plan.steps)
        }

    def _get_all_steps(self, args: Dict) -> Dict:
        """Get all steps"""
        if not self.current_plan:
            return {"status": "error", "message": "No plan loaded"}

        include_details = args.get("include_details", False)

        steps = []
        for step in self.current_plan.steps:
            step_data = {
                "id": step.id,
                "title": step.title,
                "type": step.type.value,
                "status": step.status.value,
                "priority": step.priority.value
            }

            if include_details:
                step_data.update({
                    "description": step.description,
                    "dependencies": step.dependencies,
                    "duration": step.estimated_duration,
                    "success_criteria": step.success_criteria
                })

            steps.append(step_data)

        return {
            "status": "success",
            "steps": steps,
            "count": len(steps)
        }

    def _get_next_actions(self, args: Dict) -> Dict:
        """Get next actionable steps"""
        if not self.current_plan:
            return {"status": "error", "message": "No plan loaded"}

        next_actions = self.engine.get_next_actions(self.current_plan)

        actions = []
        for step in next_actions:
            actions.append({
                "id": step.id,
                "title": step.title,
                "description": step.description,
                "priority": step.priority.value,
                "type": step.type.value,
                "duration": step.estimated_duration,
                "success_criteria": step.success_criteria
            })

        return {
            "status": "success",
            "next_actions": actions,
            "count": len(actions)
        }

    def _get_critical_path(self, args: Dict) -> Dict:
        """Get critical path"""
        if not self.current_plan:
            return {"status": "error", "message": "No plan loaded"}

        critical_steps = self.engine.get_critical_path(self.current_plan)

        path = []
        for step in critical_steps:
            path.append({
                "id": step.id,
                "title": step.title,
                "status": step.status.value,
                "priority": step.priority.value
            })

        return {
            "status": "success",
            "critical_path": path,
            "length": len(path)
        }

    def _add_step(self, args: Dict) -> Dict:
        """Add a new step"""
        if not self.current_plan:
            return {"status": "error", "message": "No plan loaded"}

        step = Step(
            id=0,
            title=args["title"],
            description=args["description"],
            type=StepType(args.get("type", "action")),
            priority=Priority(args.get("priority", "medium")),
            status=StepStatus.NOT_STARTED,
            estimated_duration=args.get("duration"),
            resources_needed=[],
            dependencies=args.get("dependencies", []),
            success_criteria=args.get("success_criteria", []),
            risks=[]
        )

        self.current_plan = self.engine.add_step(self.current_plan, step)

        return {
            "status": "success",
            "message": f"Step added: {step.title}",
            "step_id": step.id
        }

    def _update_step_status(self, args: Dict) -> Dict:
        """Update step status"""
        if not self.current_plan:
            return {"status": "error", "message": "No plan loaded"}

        step_id = args["step_id"]
        status = StepStatus(args["status"])

        self.current_plan = self.engine.update_step(
            self.current_plan,
            step_id,
            status=status
        )

        return {
            "status": "success",
            "message": f"Step {step_id} updated to {status.value}"
        }

    def _analyze_plan(self, args: Dict) -> Dict:
        """Analyze the plan"""
        if not self.current_plan:
            return {"status": "error", "message": "No plan loaded"}

        progress = self.engine.calculate_progress(self.current_plan)
        risks = self.analyzer.analyze_risks(self.current_plan)
        resources = self.analyzer.analyze_resources(self.current_plan)
        suggestions = self.analyzer.suggest_optimizations(self.current_plan)
        blockers = self.engine.get_blockers(self.current_plan)

        return {
            "status": "success",
            "progress": progress,
            "risks": {
                "total": risks["risk_count"],
                "high_priority": len(risks["high_priority_risks"]),
                "details": risks["high_priority_risks"][:5]  # Top 5
            },
            "resources": {
                "types": list(resources.keys()),
                "summary": {k: len(v) for k, v in resources.items()}
            },
            "suggestions": suggestions,
            "blockers": [
                {
                    "blocked_step": blocked.title,
                    "blocking_steps": [b.title for b in blocking]
                }
                for blocked, blocking in blockers
            ]
        }

    def _save_plan(self, args: Dict) -> Dict:
        """Save current plan"""
        if not self.current_plan:
            return {"status": "error", "message": "No plan loaded"}

        filename = args["filename"]
        if not filename.endswith('.json'):
            filename += '.json'

        filepath = self.engine.save_plan(self.current_plan, filename)

        return {
            "status": "success",
            "message": f"Plan saved to {filepath}",
            "filename": filename
        }

    def _export_markdown(self, args: Dict) -> Dict:
        """Export plan to Markdown"""
        if not self.current_plan:
            return {"status": "error", "message": "No plan loaded"}

        # This would need to be implemented similar to CLI export
        # For now, return basic structure

        return {
            "status": "success",
            "message": "Markdown export would be generated here",
            "note": "Use CLI for full markdown export functionality"
        }

    def _error(self, message: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "error": {
                "code": -1,
                "message": message
            }
        }

    def run(self):
        """Main server loop - read JSON-RPC from stdin"""
        for line in sys.stdin:
            if not line.strip():
                continue

            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                error_response = self._error(f"Invalid JSON: {e}")
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = self._error(f"Server error: {e}")
                print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    server = BackcastMCPServer()
    server.run()
