#!/home/panda/Documents/PythonScripts/OutcomeBackcasting/backcast_venv/bin/python3
"""
HTTP Server for Outcome Backcasting Engine

Exposes backcasting functionality via HTTP REST API for mobile/web access.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from backcast_engine import (
    BackcastEngine, BackcastAnalyzer,
    Outcome, Step, Resource, Risk,
    StepType, StepStatus, Priority
)

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile access

# Global state (in production, use proper session management)
engine = BackcastEngine()
analyzer = BackcastAnalyzer()
current_plan = None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Outcome Backcasting Engine',
        'version': '1.0'
    })


@app.route('/api/plans', methods=['GET'])
def list_plans():
    """List all saved plans"""
    plans = engine.list_plans()
    return jsonify({
        'status': 'success',
        'plans': plans,
        'count': len(plans)
    })


@app.route('/api/plan', methods=['POST'])
def create_plan():
    """Create a new backcasting plan"""
    data = request.json

    outcome = Outcome(
        title=data['title'],
        description=data['description'],
        success_criteria=data.get('success_criteria', []),
        constraints=data.get('constraints', []),
        timeline=data.get('timeline', 'To be determined')
    )

    global current_plan
    current_plan = engine.create_plan(outcome)

    # Generate template if requested
    num_phases = data.get('num_phases', 5)
    if num_phases > 0:
        current_plan = engine.generate_steps(current_plan, num_phases)

    return jsonify({
        'status': 'success',
        'message': f'Plan created: {outcome.title}',
        'steps_generated': len(current_plan.steps)
    })


@app.route('/api/plan/<filename>', methods=['GET'])
def load_plan(filename):
    """Load an existing plan"""
    global current_plan
    if not filename.endswith('.json'):
        filename += '.json'

    current_plan = engine.load_plan(filename)
    return jsonify({
        'status': 'success',
        'message': f'Plan loaded: {current_plan.outcome.title}',
        'steps': len(current_plan.steps)
    })


@app.route('/api/plan/overview', methods=['GET'])
def get_overview():
    """Get plan overview"""
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    progress = engine.calculate_progress(current_plan)

    return jsonify({
        'status': 'success',
        'outcome': {
            'title': current_plan.outcome.title,
            'description': current_plan.outcome.description,
            'timeline': current_plan.outcome.timeline,
            'success_criteria': current_plan.outcome.success_criteria,
            'constraints': current_plan.outcome.constraints
        },
        'progress': progress,
        'total_steps': len(current_plan.steps)
    })


@app.route('/api/plan/steps', methods=['GET'])
def get_all_steps():
    """Get all steps"""
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    include_details = request.args.get('details', 'false').lower() == 'true'

    steps = []
    for step in current_plan.steps:
        step_data = {
            'id': step.id,
            'title': step.title,
            'type': step.type.value,
            'status': step.status.value,
            'priority': step.priority.value
        }

        if include_details:
            step_data.update({
                'description': step.description,
                'dependencies': step.dependencies,
                'duration': step.estimated_duration,
                'success_criteria': step.success_criteria
            })

        steps.append(step_data)

    return jsonify({
        'status': 'success',
        'steps': steps,
        'count': len(steps)
    })


@app.route('/api/plan/next-actions', methods=['GET'])
def get_next_actions():
    """Get next actionable steps"""
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    next_actions = engine.get_next_actions(current_plan)

    actions = []
    for step in next_actions:
        actions.append({
            'id': step.id,
            'title': step.title,
            'description': step.description,
            'priority': step.priority.value,
            'type': step.type.value,
            'duration': step.estimated_duration,
            'success_criteria': step.success_criteria
        })

    return jsonify({
        'status': 'success',
        'next_actions': actions,
        'count': len(actions)
    })


@app.route('/api/plan/critical-path', methods=['GET'])
def get_critical_path():
    """Get critical path"""
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    critical_steps = engine.get_critical_path(current_plan)

    path = []
    for step in critical_steps:
        path.append({
            'id': step.id,
            'title': step.title,
            'status': step.status.value,
            'priority': step.priority.value
        })

    return jsonify({
        'status': 'success',
        'critical_path': path,
        'length': len(path)
    })


@app.route('/api/plan/step', methods=['POST'])
def add_step():
    """Add a new step"""
    global current_plan
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    data = request.json

    step = Step(
        id=0,
        title=data['title'],
        description=data['description'],
        type=StepType(data.get('type', 'action')),
        priority=Priority(data.get('priority', 'medium')),
        status=StepStatus.NOT_STARTED,
        estimated_duration=data.get('duration'),
        resources_needed=[],
        dependencies=data.get('dependencies', []),
        success_criteria=data.get('success_criteria', []),
        risks=[]
    )

    current_plan = engine.add_step(current_plan, step)

    return jsonify({
        'status': 'success',
        'message': f'Step added: {step.title}',
        'step_id': step.id
    })


@app.route('/api/plan/step/<int:step_id>/status', methods=['PUT'])
def update_step_status(step_id):
    """Update step status"""
    global current_plan
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    data = request.json
    status = StepStatus(data['status'])

    current_plan = engine.update_step(
        current_plan,
        step_id,
        status=status
    )

    return jsonify({
        'status': 'success',
        'message': f'Step {step_id} updated to {status.value}'
    })


@app.route('/api/plan/analyze', methods=['GET'])
def analyze_plan():
    """Analyze the plan"""
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    progress = engine.calculate_progress(current_plan)
    risks = analyzer.analyze_risks(current_plan)
    resources = analyzer.analyze_resources(current_plan)
    suggestions = analyzer.suggest_optimizations(current_plan)
    blockers = engine.get_blockers(current_plan)

    return jsonify({
        'status': 'success',
        'progress': progress,
        'risks': {
            'total': risks['risk_count'],
            'high_priority': len(risks['high_priority_risks']),
            'details': risks['high_priority_risks'][:5]
        },
        'resources': {
            'types': list(resources.keys()),
            'summary': {k: len(v) for k, v in resources.items()}
        },
        'suggestions': suggestions,
        'blockers': [
            {
                'blocked_step': blocked.title,
                'blocking_steps': [b.title for b in blocking]
            }
            for blocked, blocking in blockers
        ]
    })


@app.route('/api/plan/save', methods=['POST'])
def save_plan():
    """Save current plan"""
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    data = request.json
    filename = data['filename']
    if not filename.endswith('.json'):
        filename += '.json'

    filepath = engine.save_plan(current_plan, filename)

    return jsonify({
        'status': 'success',
        'message': f'Plan saved to {filepath}',
        'filename': filename
    })


if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) so it's accessible from mobile
    app.run(host='0.0.0.0', port=8080, debug=True)
