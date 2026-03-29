#!/home/panda/Documents/PythonScripts/OutcomeBackcasting/backcast_venv/bin/python3
"""
HTTP Server for Outcome Backcasting Engine

Exposes backcasting functionality via HTTP REST API for mobile/web access.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
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
                'success_criteria': step.success_criteria,
                'resources_needed': [
                    {'name': r.name, 'type': r.type, 'amount': r.amount}
                    for r in step.resources_needed
                ] if step.resources_needed else [],
                'risks': [
                    {'description': r.description, 'probability': r.probability, 'impact': r.impact, 'mitigation': r.mitigation}
                    for r in step.risks
                ] if step.risks else [],
                'notes': step.notes
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


@app.route('/api/plan/reorder', methods=['PUT'])
def reorder_step():
    """Reorder a step to a new position"""
    global current_plan
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    data = request.json
    step_id = data['step_id']
    new_position = data['new_position']

    step = None
    for i, s in enumerate(current_plan.steps):
        if s.id == step_id:
            step = current_plan.steps.pop(i)
            break

    if not step:
        return jsonify({'status': 'error', 'message': 'Step not found'}), 404

    new_position = max(0, min(new_position, len(current_plan.steps)))
    current_plan.steps.insert(new_position, step)

    return jsonify({'status': 'success', 'message': f'Step {step_id} moved to position {new_position}'})


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


@app.route('/api/plan/generate-ai', methods=['POST'])
def generate_ai_steps():
    """Generate AI-enhanced steps for the current plan"""
    global current_plan
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    data = request.json or {}
    num_steps = data.get('num_steps', 10)

    try:
        current_plan = engine.generate_ai_steps(current_plan, num_steps=num_steps)
        return jsonify({
            'status': 'success',
            'message': f'Generated {len(current_plan.steps)} AI-enhanced steps',
            'steps_count': len(current_plan.steps)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/plan/export/pdf', methods=['POST'])
def export_pdf():
    """Export plan to PDF"""
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    data = request.get_json(silent=True) or {}
    filename = data.get('filename')

    try:
        filepath = engine.export_to_pdf(current_plan, filename)
        return jsonify({
            'status': 'success',
            'message': 'PDF exported',
            'filepath': filepath,
            'filename': os.path.basename(filepath)
        })
    except ImportError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/plan/export/ical', methods=['POST'])
def export_ical():
    """Export plan to iCal"""
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    data = request.get_json(silent=True) or {}
    filename = data.get('filename')

    try:
        filepath = engine.export_to_ical(current_plan, filename)
        return jsonify({
            'status': 'success',
            'message': 'iCal exported',
            'filepath': filepath,
            'filename': os.path.basename(filepath)
        })
    except ImportError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/plan/export/html', methods=['POST'])
def export_html():
    """Export plan to HTML report"""
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    data = request.get_json(silent=True) or {}
    filename = data.get('filename')

    try:
        filepath = engine.export_to_html(current_plan, filename)
        return jsonify({
            'status': 'success',
            'message': 'HTML exported',
            'filepath': filepath,
            'filename': os.path.basename(filepath)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/exports/<filename>')
def serve_export(filename):
    """Serve exported files"""
    from flask import send_from_directory
    return send_from_directory(engine.data_dir, filename)


@app.route('/')
def dashboard():
    """Serve the web dashboard"""
    return DASHBOARD_HTML


# Web Dashboard HTML
DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backcasting Dashboard</title>
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg: #08080c;
            --surface-0: #0c0c14;
            --surface-1: #111119;
            --surface-2: #181824;
            --surface-3: #222233;
            --border: rgba(255,255,255,0.06);
            --border-hover: rgba(255,255,255,0.12);
            --accent: #7c5cfc;
            --accent-light: #9b7dff;
            --accent-glow: rgba(124,92,252,0.2);
            --accent-subtle: rgba(124,92,252,0.08);
            --success: #34d399;
            --success-subtle: rgba(52,211,153,0.08);
            --warning: #fbbf24;
            --error: #f87171;
            --text-primary: #eaeaf0;
            --text-secondary: #8888a0;
            --text-muted: #50506a;
            --radius: 12px;
            --radius-sm: 8px;
            --transition: 150ms ease;
        }

        [data-theme="light"] {
            --bg: #f8f8fc;
            --surface-0: #ffffff;
            --surface-1: #ffffff;
            --surface-2: #f0f0f6;
            --surface-3: #e8e8f0;
            --border: rgba(0,0,0,0.08);
            --border-hover: rgba(0,0,0,0.15);
            --accent: #6b4ce6;
            --accent-light: #8b6cf0;
            --accent-glow: rgba(107,76,230,0.15);
            --accent-subtle: rgba(107,76,230,0.06);
            --success: #22b47f;
            --success-subtle: rgba(34,180,127,0.08);
            --warning: #d4960c;
            --error: #e04545;
            --text-primary: #1a1a2e;
            --text-secondary: #6b6b80;
            --text-muted: #9898ac;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            min-height: 100vh;
            color: var(--text-primary);
            font-size: 14px;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            overflow: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: -200px;
            left: 50%;
            transform: translateX(-50%);
            width: 600px;
            height: 400px;
            background: radial-gradient(ellipse, rgba(124,92,252,0.06) 0%, transparent 70%);
            pointer-events: none;
            z-index: 0;
        }

        [data-theme="light"] body::before {
            background: radial-gradient(ellipse, rgba(107,76,230,0.04) 0%, transparent 70%);
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

        .layout {
            display: grid;
            grid-template-columns: 260px 1fr;
            height: 100vh;
            position: relative;
            z-index: 1;
            transition: grid-template-columns 200ms ease;
        }
        .layout.collapsed { grid-template-columns: 60px 1fr; }

        @media (max-width: 768px) {
            .layout { grid-template-columns: 1fr; }
            .sidebar { display: none; }
            .sidebar.mobile-open { display: flex; position: fixed; inset: 0; z-index: 50; width: 280px; }
        }

        .sidebar {
            background: var(--surface-0);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 200ms ease;
        }

        .sidebar-brand {
            padding: 20px 20px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
        }
        .collapsed .sidebar-brand { padding: 16px 12px; justify-content: center; }

        .brand-mark {
            display: flex;
            align-items: center;
            gap: 10px;
            overflow: hidden;
        }

        .brand-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: linear-gradient(135deg, var(--accent), var(--accent-light));
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            box-shadow: 0 2px 8px var(--accent-glow);
        }
        .brand-icon svg { width: 18px; height: 18px; color: white; stroke: white; fill: none; }

        .brand-name {
            font-size: 15px;
            font-weight: 600;
            letter-spacing: -0.02em;
            white-space: nowrap;
        }
        .collapsed .brand-name { display: none; }

        .collapse-btn {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: transparent;
            color: var(--text-muted);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            transition: all 150ms;
            flex-shrink: 0;
        }
        .collapse-btn:hover { background: var(--surface-2); color: var(--text-secondary); }
        .collapsed .collapse-btn { display: none; }

        .sidebar-section {
            padding: 16px 12px;
            flex: 1;
            overflow-y: auto;
        }

        .sidebar-label {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--text-muted);
            padding: 0 8px;
            margin-bottom: 8px;
        }
        .collapsed .sidebar-label { display: none; }

        .plan-list { list-style: none; display: flex; flex-direction: column; gap: 2px; }

        .plan-item {
            padding: 10px 12px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all 150ms;
            color: var(--text-secondary);
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
            border: none;
            background: none;
            width: 100%;
            text-align: left;
            font-family: inherit;
        }
        .plan-item:hover { background: var(--surface-2); color: var(--text-primary); }
        .plan-item.active {
            background: var(--accent-subtle);
            color: var(--accent-light);
            font-weight: 500;
        }
        .plan-item .plan-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--text-muted);
            flex-shrink: 0;
        }
        .plan-item.active .plan-dot { background: var(--accent); box-shadow: 0 0 6px var(--accent-glow); }
        .plan-item .plan-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .collapsed .plan-name { display: none; }
        .collapsed .plan-item { justify-content: center; padding: 10px 0; }

        .sidebar-footer {
            padding: 12px;
            border-top: 1px solid var(--border);
            flex-shrink: 0;
        }

        .new-plan-btn {
            width: 100%;
            padding: 10px;
            border-radius: var(--radius-sm);
            border: 1px dashed var(--border-hover);
            background: transparent;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 13px;
            font-family: inherit;
            transition: all 150ms;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .new-plan-btn:hover { border-color: var(--accent); color: var(--accent-light); background: var(--accent-subtle); }
        .collapsed .new-plan-btn span { display: none; }

        /* Main area */
        .main {
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .main-header {
            padding: 12px 32px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--surface-0);
            flex-shrink: 0;
        }

        .header-left { display: flex; align-items: center; gap: 16px; }

        .search-box {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: var(--surface-1);
            color: var(--text-muted);
            font-size: 13px;
            min-width: 220px;
            cursor: text;
            transition: all 150ms;
        }
        .search-box:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
        .search-box input {
            border: none;
            background: none;
            color: var(--text-primary);
            font-size: 13px;
            font-family: inherit;
            outline: none;
            flex: 1;
            min-width: 0;
        }
        .search-box input::placeholder { color: var(--text-muted); }
        .search-box kbd {
            font-size: 11px;
            padding: 1px 5px;
            border-radius: 4px;
            background: var(--surface-3);
            border: 1px solid var(--border);
            color: var(--text-muted);
            font-family: inherit;
        }
        .search-box svg { flex-shrink: 0; color: var(--text-muted); }

        .header-right { display: flex; align-items: center; gap: 6px; }

        .icon-btn {
            width: 36px;
            height: 36px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: transparent;
            color: var(--text-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 150ms;
            font-size: 16px;
            font-family: inherit;
        }
        .icon-btn:hover { background: var(--surface-2); color: var(--text-primary); }
        .icon-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

        .main-scroll {
            flex: 1;
            overflow-y: auto;
            padding: 32px;
        }

        /* Section headings */
        .section-label {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .section-label::after {
            content: '';
            flex: 1;
            height: 1px;
            background: var(--border);
        }

        /* Plan header */
        .plan-header { margin-bottom: 28px; }
        .plan-header h2 {
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin-bottom: 6px;
            color: var(--text-primary);
        }
        .plan-meta {
            display: flex;
            align-items: center;
            gap: 16px;
            color: var(--text-secondary);
            font-size: 13px;
        }
        .plan-meta .sep { color: var(--text-muted); }

        /* Stats row */
        .stats-row {
            display: flex;
            gap: 16px;
            margin-bottom: 28px;
        }

        .progress-ring-card {
            background: var(--surface-1);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 24px;
            display: flex;
            align-items: center;
            gap: 24px;
            min-width: 280px;
            flex-shrink: 0;
        }

        .ring-container {
            position: relative;
            width: 100px;
            height: 100px;
            flex-shrink: 0;
        }

        .ring-svg { width: 100px; height: 100px; transform: rotate(-90deg); }
        .ring-bg { fill: none; stroke: var(--surface-3); stroke-width: 8; }
        .ring-progress {
            fill: none;
            stroke: url(#ringGradient);
            stroke-width: 8;
            stroke-linecap: round;
            stroke-dasharray: 251.2;
            stroke-dashoffset: 251.2;
            transition: stroke-dashoffset 800ms cubic-bezier(0.4, 0, 0.2, 1);
        }

        .ring-label {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .ring-value { font-size: 28px; font-weight: 700; letter-spacing: -0.03em; line-height: 1; }
        .ring-subtitle { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }

        .ring-details { display: flex; flex-direction: column; gap: 10px; }
        .ring-detail { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-secondary); }
        .ring-detail .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
        .ring-detail .count { font-weight: 600; color: var(--text-primary); margin-left: auto; min-width: 20px; text-align: right; }

        .mini-stats { display: flex; flex: 1; gap: 12px; }

        .mini-stat {
            flex: 1;
            background: var(--surface-1);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px;
            position: relative;
            overflow: hidden;
        }
        .mini-stat::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
        .mini-stat.stat-next::before { background: var(--success); }
        .mini-stat.stat-blocked::before { background: var(--error); }
        .mini-stat.stat-timeline::before { background: var(--warning); }

        .mini-stat-value { font-size: 20px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 4px; }
        .mini-stat-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }

        @media (max-width: 900px) {
            .stats-row { flex-direction: column; }
            .mini-stats { flex-direction: row; }
        }

        /* Action bar */
        .action-bar {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .action-btn {
            padding: 8px 16px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: var(--surface-1);
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 13px;
            font-family: inherit;
            font-weight: 500;
            transition: all 150ms;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            line-height: 1;
        }
        .action-btn:hover { background: var(--surface-2); color: var(--text-primary); border-color: var(--border-hover); }
        .action-btn:active { transform: scale(0.97); }
        .action-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
        .action-btn.primary {
            background: var(--accent);
            border-color: var(--accent);
            color: white;
            box-shadow: 0 2px 8px var(--accent-glow);
        }
        .action-btn.primary:hover { background: var(--accent-light); }

        .filter-pills {
            display: flex;
            gap: 2px;
            margin-left: auto;
            background: var(--surface-1);
            border-radius: var(--radius-sm);
            padding: 3px;
            border: 1px solid var(--border);
        }
        .filter-pill {
            padding: 5px 12px;
            border-radius: 6px;
            border: none;
            background: transparent;
            color: var(--text-muted);
            font-size: 12px;
            font-family: inherit;
            font-weight: 500;
            cursor: pointer;
            transition: all 150ms;
        }
        .filter-pill:hover { color: var(--text-secondary); }
        .filter-pill.active { background: var(--surface-3); color: var(--text-primary); }

        /* Step cards */
        .step-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .step-card {
            background: var(--surface-1);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 14px 20px;
            display: flex;
            align-items: center;
            gap: 14px;
            transition: all 150ms;
            cursor: pointer;
        }
        .step-card:hover {
            background: var(--surface-2);
            border-color: var(--border-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .step-drag {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1.5px;
            color: var(--text-muted);
            cursor: grab;
            flex-shrink: 0;
            opacity: 0;
            transition: opacity 150ms;
            padding: 4px 2px;
        }
        .step-card:hover .step-drag { opacity: 1; }
        .drag-dot {
            width: 3px;
            height: 3px;
            border-radius: 50%;
            background: currentColor;
        }
        .drag-row { display: flex; gap: 3px; }

        .step-ring {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            border: 2px solid var(--text-muted);
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 150ms;
            cursor: pointer;
            font-size: 11px;
            font-weight: 700;
        }
        .step-ring:hover { border-color: var(--text-secondary); }
        .step-ring.completed { border-color: var(--success); background: var(--success); color: white; }
        .step-ring.in_progress { border-color: var(--accent); background: var(--accent-subtle); }
        .step-ring.in_progress::after { content: ''; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
        .step-ring.blocked { border-color: var(--error); background: rgba(248,113,113,0.1); color: var(--error); }

        .step-body { flex: 1; min-width: 0; }
        .step-card-title { font-size: 14px; font-weight: 500; color: var(--text-primary); }
        .step-card-desc {
            font-size: 12px;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-top: 2px;
        }

        .step-card.completed .step-card-title { color: var(--text-secondary); text-decoration: line-through; text-decoration-color: var(--text-muted); }
        .step-card.completed .step-card-desc { color: var(--text-muted); }

        .step-priority {
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 500;
            flex-shrink: 0;
        }
        .step-priority.critical { background: rgba(248,113,113,0.1); color: var(--error); }
        .step-priority.high { background: rgba(251,191,36,0.1); color: var(--warning); }
        .step-priority.medium { background: rgba(124,92,252,0.1); color: var(--accent-light); }
        .step-priority.low { background: rgba(136,136,160,0.1); color: var(--text-secondary); }

        .step-hover-actions {
            display: flex;
            gap: 4px;
            opacity: 0;
            transition: opacity 150ms;
            flex-shrink: 0;
        }
        .step-card:hover .step-hover-actions { opacity: 1; }

        .step-action-btn {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: var(--surface-2);
            color: var(--text-muted);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            transition: all 150ms;
            font-family: inherit;
        }
        .step-action-btn:hover { background: var(--surface-3); color: var(--text-primary); }
        .step-action-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

        /* Export menu */
        .export-menu {
            position: fixed;
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 4px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            z-index: 50;
            display: none;
        }
        .export-menu.open { display: block; }
        .export-menu button {
            display: block;
            width: 100%;
            padding: 8px 16px;
            border: none;
            background: none;
            color: var(--text-secondary);
            font-size: 13px;
            font-family: inherit;
            text-align: left;
            cursor: pointer;
            border-radius: 4px;
            transition: all 150ms;
        }
        .export-menu button:hover { background: var(--surface-3); color: var(--text-primary); }

        .btn-primary {
            background: var(--accent);
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: var(--radius-sm);
            font-size: 14px;
            font-weight: 500;
            font-family: inherit;
            cursor: pointer;
            transition: all 150ms;
            box-shadow: 0 2px 8px var(--accent-glow);
        }
        .btn-primary:hover { background: var(--accent-light); }

        .step-expanded {
            background: var(--surface-1);
            border: 1px solid var(--accent);
            border-radius: var(--radius);
            padding: 20px;
            margin-bottom: 6px;
            box-shadow: 0 0 0 1px var(--accent-subtle), 0 8px 24px rgba(0,0,0,0.2);
            animation: expandIn 200ms ease;
        }
        @keyframes expandIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

        .step-expanded-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }

        .step-expanded-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        @media (max-width: 600px) { .step-expanded-grid { grid-template-columns: 1fr; } }

        .detail-section h4 {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 8px;
        }
        .detail-section p, .detail-section li {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.6;
        }
        .detail-section ul { list-style: none; padding: 0; margin: 0; }
        .detail-section li { padding: 2px 0; }
        .detail-section li::before { content: '\\2192  '; color: var(--accent); }
        .detail-empty { color: var(--text-muted); font-style: italic; font-size: 12px; }

        .shortcuts-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 100;
            display: none;
            align-items: center;
            justify-content: center;
        }
        .shortcuts-overlay.active { display: flex; }

        .shortcuts-card {
            background: var(--surface-1);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 24px 28px;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 24px 48px rgba(0,0,0,0.4);
        }
        .shortcuts-card h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }

        .shortcut-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
            color: var(--text-secondary);
        }
        .shortcut-row:last-child { border-bottom: none; }
        .shortcut-row kbd {
            padding: 3px 8px;
            border-radius: 4px;
            background: var(--surface-3);
            border: 1px solid var(--border);
            font-size: 12px;
            font-family: inherit;
            color: var(--text-primary);
            min-width: 28px;
            text-align: center;
        }

        .shortcut-hint {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 8px 14px;
            border-radius: var(--radius-sm);
            background: var(--surface-2);
            border: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            transition: all 150ms;
            z-index: 10;
        }
        .shortcut-hint:hover { color: var(--text-secondary); border-color: var(--border-hover); }
        .shortcut-hint kbd {
            padding: 2px 6px;
            border-radius: 4px;
            background: var(--surface-3);
            border: 1px solid var(--border);
            font-size: 11px;
            font-family: inherit;
        }

        /* Modals */
        .modal {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 100;
            align-items: center;
            justify-content: center;
        }
        .modal.active { display: flex; }

        .modal-content {
            background: var(--surface-1);
            border-radius: 12px;
            padding: 24px;
            max-width: 480px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid var(--border);
            box-shadow: 0 24px 48px rgba(0,0,0,0.4);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-header h2 {
            font-size: 16px;
            font-weight: 600;
            letter-spacing: -0.02em;
        }

        .modal-close {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 20px;
            cursor: pointer;
            width: 32px;
            height: 32px;
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all var(--transition);
        }
        .modal-close:hover { background: var(--surface-2); color: var(--text-primary); }

        .form-group { margin-bottom: 16px; }
        .form-group label {
            display: block;
            margin-bottom: 6px;
            color: var(--text-secondary);
            font-size: 12px;
            font-weight: 500;
        }
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 10px 12px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: var(--surface-2);
            color: var(--text-primary);
            font-size: 13px;
            font-family: inherit;
            transition: all var(--transition);
            outline: none;
        }
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }
        .form-group textarea { min-height: 80px; resize: vertical; }
        .form-group input::placeholder,
        .form-group textarea::placeholder { color: var(--text-muted); }

        /* Toasts */
        .toast {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            padding: 10px 20px;
            border-radius: 999px;
            color: white;
            font-weight: 500;
            font-size: 13px;
            z-index: 200;
            animation: toastIn 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        .toast::before {
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .toast-success { background: var(--surface-2); border: 1px solid rgba(52,211,153,0.3); }
        .toast-success::before { background: var(--success); box-shadow: 0 0 6px var(--success); }
        .toast-error { background: var(--surface-2); border: 1px solid rgba(248,113,113,0.3); }
        .toast-error::before { background: var(--error); box-shadow: 0 0 6px var(--error); }

        @keyframes toastIn {
            from { transform: translateX(-50%) translateY(16px); opacity: 0; }
            to { transform: translateX(-50%) translateY(0); opacity: 1; }
        }

        /* Empty states */
        .empty-state {
            text-align: center;
            padding: 48px 24px;
            color: var(--text-muted);
        }
        .empty-state h2 {
            font-size: 16px;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }
        .empty-state p {
            font-size: 13px;
            color: var(--text-muted);
        }

        /* Next actions callout */
        .next-actions {
            background: rgba(52,211,153,0.06);
            border: 1px solid rgba(52,211,153,0.15);
            border-radius: var(--radius);
            padding: 16px 20px;
            margin-bottom: 24px;
        }
        .next-actions h3 {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--success);
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .next-actions h3::before {
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 6px var(--success);
        }
        .next-actions ul { list-style: none; }
        .next-actions li {
            padding: 6px 0;
            font-size: 13px;
            color: var(--text-primary);
            border-bottom: 1px solid rgba(52,211,153,0.08);
        }
        .next-actions li:last-child { border-bottom: none; }
    </style>
</head>
<body>
    <div class="layout" id="appLayout">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-brand">
                <div class="brand-mark">
                    <div class="brand-icon">
                        <svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
                    </div>
                    <span class="brand-name">Backcasting</span>
                </div>
                <button class="collapse-btn" onclick="toggleSidebar()" aria-label="Collapse sidebar">&#9665;</button>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Plans</div>
                <ul class="plan-list" id="planList">
                    <li style="padding:16px;color:var(--text-muted);">Loading plans...</li>
                </ul>
            </div>
            <div class="sidebar-footer">
                <button class="new-plan-btn" onclick="showCreateModal()">+<span> New Plan</span></button>
            </div>
        </aside>

        <div class="main">
            <header class="main-header">
                <div class="header-left">
                    <div class="search-box">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                        <input type="text" id="searchInput" placeholder="Search steps..." aria-label="Search steps">
                        <kbd>/</kbd>
                    </div>
                </div>
                <div class="header-right">
                    <button class="icon-btn" onclick="toggleTheme()" id="themeToggle" aria-label="Toggle theme" title="Toggle theme">
                        <svg id="themeIcon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                    </button>
                    <button class="icon-btn" onclick="showShortcuts()" aria-label="Keyboard shortcuts" title="Keyboard shortcuts">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h.001M10 8h.001M14 8h.001M18 8h.001M8 12h.001M12 12h.001M16 12h.001M7 16h10"/></svg>
                    </button>
                </div>
            </header>

            <div class="main-scroll">
                <div id="noPlanSelected" class="empty-state">
                    <h2>Select or create a plan</h2>
                    <p>Choose a plan from the sidebar to get started</p>
                </div>

                <div id="planDetails" style="display:none;">
                <div class="plan-header">
                    <h2 id="planTitle"></h2>
                    <div class="plan-meta" id="planMeta"></div>
                </div>

                <div class="stats-row">
                    <div class="progress-ring-card">
                        <div class="ring-container">
                            <svg class="ring-svg" viewBox="0 0 100 100">
                                <defs>
                                    <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stop-color="#7c5cfc"/>
                                        <stop offset="100%" stop-color="#34d399"/>
                                    </linearGradient>
                                </defs>
                                <circle class="ring-bg" cx="50" cy="50" r="40"/>
                                <circle class="ring-progress" id="ringProgress" cx="50" cy="50" r="40"/>
                            </svg>
                            <div class="ring-label">
                                <span class="ring-value" id="ringPercent">0%</span>
                                <span class="ring-subtitle">Done</span>
                            </div>
                        </div>
                        <div class="ring-details">
                            <div class="ring-detail"><span class="dot" style="background:var(--success)"></span>Completed<span class="count" id="statDone">0</span></div>
                            <div class="ring-detail"><span class="dot" style="background:var(--accent)"></span>In Progress<span class="count" id="statProgress">0</span></div>
                            <div class="ring-detail"><span class="dot" style="background:var(--error)"></span>Blocked<span class="count" id="statBlocked">0</span></div>
                            <div class="ring-detail"><span class="dot" style="background:var(--text-muted)"></span>To Do<span class="count" id="statTodo">0</span></div>
                        </div>
                    </div>
                    <div class="mini-stats">
                        <div class="mini-stat stat-next">
                            <div class="mini-stat-value" id="statNextActions">0</div>
                            <div class="mini-stat-label">Next Actions</div>
                        </div>
                        <div class="mini-stat stat-blocked">
                            <div class="mini-stat-value" id="statBlockedCount">0</div>
                            <div class="mini-stat-label">Blocked</div>
                        </div>
                        <div class="mini-stat stat-timeline">
                            <div class="mini-stat-value" id="statTimeline">&mdash;</div>
                            <div class="mini-stat-label">Timeline</div>
                        </div>
                    </div>
                </div>

                <div class="action-bar">
                    <button class="action-btn primary" onclick="showAddStepModal()">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
                        Add Step
                    </button>
                    <button class="action-btn" onclick="generateAISteps()">AI Generate</button>
                    <button class="action-btn" onclick="showExportMenu(event)">Export &#9662;</button>
                    <div class="filter-pills" role="tablist">
                        <button class="filter-pill active" role="tab" aria-selected="true" onclick="setFilter('all', this)">All</button>
                        <button class="filter-pill" role="tab" aria-selected="false" onclick="setFilter('not_started', this)">To Do</button>
                        <button class="filter-pill" role="tab" aria-selected="false" onclick="setFilter('in_progress', this)">Active</button>
                        <button class="filter-pill" role="tab" aria-selected="false" onclick="setFilter('completed', this)">Done</button>
                        <button class="filter-pill" role="tab" aria-selected="false" onclick="setFilter('blocked', this)">Blocked</button>
                    </div>
                </div>
                <div class="step-list" id="stepList"></div>
                <div class="export-menu" id="exportMenu">
                    <button onclick="exportPDF(); closeExportMenu()">PDF</button>
                    <button onclick="exportHTML(); closeExportMenu()">HTML</button>
                    <button onclick="exportICal(); closeExportMenu()">iCal</button>
                </div>
            </div>
        </main>
    </div>

    <!-- Create Plan Modal -->
    <div class="modal" id="createModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Create New Plan</h2>
                <button class="modal-close" onclick="closeModal('createModal')">&times;</button>
            </div>
            <form onsubmit="createPlan(event)">
                <div class="form-group">
                    <label>Title *</label>
                    <input type="text" id="newTitle" required placeholder="e.g., Launch my startup">
                </div>
                <div class="form-group">
                    <label>Description *</label>
                    <textarea id="newDescription" required placeholder="Describe your desired outcome in detail"></textarea>
                </div>
                <div class="form-group">
                    <label>Timeline</label>
                    <input type="text" id="newTimeline" placeholder="e.g., 6 months">
                </div>
                <div class="form-group">
                    <label>Success Criteria (comma-separated)</label>
                    <input type="text" id="newCriteria" placeholder="e.g., 1000 users, Profitable">
                </div>
                <div class="form-group">
                    <label>Use AI to generate steps?</label>
                    <select id="useAI">
                        <option value="yes">Yes - AI enhanced steps</option>
                        <option value="no">No - Template steps</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%">Create Plan</button>
            </form>
        </div>
    </div>

    <!-- Add Step Modal -->
    <div class="modal" id="addStepModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Add Step</h2>
                <button class="modal-close" onclick="closeModal('addStepModal')">&times;</button>
            </div>
            <form onsubmit="addStep(event)">
                <div class="form-group">
                    <label>Title *</label>
                    <input type="text" id="stepTitle" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="stepDescription"></textarea>
                </div>
                <div class="form-group">
                    <label>Priority</label>
                    <select id="stepPriority">
                        <option value="medium">Medium</option>
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="low">Low</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Duration</label>
                    <input type="text" id="stepDuration" placeholder="e.g., 2 weeks">
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%">Add Step</button>
            </form>
        </div>
    </div>

    <script>
        const API = '';
        let currentPlan = null;

        async function api(endpoint, options = {}) {
            const res = await fetch(API + endpoint, {
                headers: { 'Content-Type': 'application/json', ...options.headers },
                ...options
            });
            return res.json();
        }

        function toggleSidebar() {
            var layout = document.getElementById('appLayout');
            var collapsed = layout.classList.toggle('collapsed');
            localStorage.setItem('sidebar-collapsed', collapsed);
            document.querySelector('.collapse-btn').textContent = collapsed ? '\u25B7' : '\u25C1';
        }

        // Restore sidebar state on load
        (function() {
            if (localStorage.getItem('sidebar-collapsed') === 'true') {
                document.getElementById('appLayout').classList.add('collapsed');
                var btn = document.querySelector('.collapse-btn');
                if (btn) btn.textContent = '\u25B7';
            }
        })();

        function toggleTheme() {
            var html = document.documentElement;
            var current = html.getAttribute('data-theme');
            var next = current === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateThemeIcon(next);
        }

        function updateThemeIcon(theme) {
            var icon = document.getElementById('themeIcon');
            if (theme === 'light') {
                icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
            } else {
                icon.innerHTML = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
            }
        }

        // Restore theme on load
        (function() {
            var saved = localStorage.getItem('theme') || 'dark';
            if (saved === 'light') {
                document.documentElement.setAttribute('data-theme', 'light');
                updateThemeIcon('light');
            }
        })();

        function toast(msg, type = 'success') {
            const t = document.createElement('div');
            t.className = 'toast toast-' + type;
            t.textContent = msg;
            document.body.appendChild(t);
            setTimeout(() => t.remove(), 3000);
        }

        async function loadPlans() {
            const data = await api('/api/plans');
            const list = document.getElementById('planList');
            if (data.plans && data.plans.length > 0) {
                list.innerHTML = data.plans.map(p =>
                    `<li class="plan-item" onclick="loadPlan('${p}')">${p.replace('.json','')}</li>`
                ).join('');
            } else {
                list.innerHTML = '<li class="empty-state" style="padding:16px;">No plans yet</li>';
            }
        }

        async function loadPlan(filename) {
            const data = await api('/api/plan/' + filename);
            if (data.status === 'success') {
                currentPlan = filename;
                document.querySelectorAll('.plan-item').forEach(el => el.classList.remove('active'));
                event?.target?.classList.add('active');
                await refreshPlanView();
            }
        }

        async function refreshPlanView() {
            const overview = await api('/api/plan/overview');
            const steps = await api('/api/plan/steps?details=true');
            const nextActions = await api('/api/plan/next-actions');

            document.getElementById('noPlanSelected').style.display = 'none';
            document.getElementById('planDetails').style.display = 'block';

            const p = overview.progress;
            document.getElementById('planTitle').textContent = overview.outcome.title;
            document.getElementById('planMeta').innerHTML =
                '<span>' + overview.total_steps + ' steps</span>' +
                '<span class="sep">&middot;</span>' +
                '<span>' + (overview.outcome.timeline || 'No timeline') + '</span>' +
                '<span class="sep">&middot;</span>' +
                '<span style="color:var(--success)">' + p.percent + '% complete</span>';

            // Progress ring
            const circumference = 251.2;
            const offset = circumference - (circumference * p.percent / 100);
            document.getElementById('ringProgress').style.strokeDashoffset = offset;
            document.getElementById('ringPercent').textContent = p.percent + '%';
            document.getElementById('statDone').textContent = p.completed;
            document.getElementById('statProgress').textContent = p.in_progress;
            document.getElementById('statBlocked').textContent = p.blocked;
            document.getElementById('statTodo').textContent = p.not_started;

            // Mini stats
            document.getElementById('statNextActions').textContent = nextActions.next_actions ? nextActions.next_actions.length : 0;
            document.getElementById('statBlockedCount').textContent = p.blocked;
            document.getElementById('statTimeline').textContent = overview.outcome.timeline || '\u2014';

            // Steps
            const stepList = document.getElementById('stepList');
            if (steps.steps && steps.steps.length > 0) {
                window._allSteps = steps.steps;
                renderSteps(steps.steps);
            } else {
                stepList.innerHTML = '<div class="empty-state"><p>No steps yet. Click "Add Step" or "AI Generate" to get started.</p></div>';
            }
        }

        async function updateStatus(stepId, status) {
            await api('/api/plan/step/' + stepId + '/status', {
                method: 'PUT',
                body: JSON.stringify({ status })
            });
            await api('/api/plan/save', { method: 'POST', body: JSON.stringify({ filename: currentPlan }) });

            if (status === 'completed') {
                var card = document.querySelector('[data-step-id="' + stepId + '"]');
                if (card) {
                    var rect = card.getBoundingClientRect();
                    fireConfetti(rect.left + 30, rect.top + rect.height / 2, 25);
                }
                var overview = await api('/api/plan/overview');
                if (overview.progress && overview.progress.percent === 100) {
                    setTimeout(function() {
                        fireConfetti(window.innerWidth / 2, window.innerHeight / 2, 120);
                        toast('All steps complete!');
                    }, 400);
                }
            }

            toast('Status updated');
            refreshPlanView();
        }

        let currentFilter = 'all';
        let searchQuery = '';
        let expandedStepId = null;

        function renderSteps(steps) {
            const stepList = document.getElementById('stepList');
            let filtered = steps;

            if (currentFilter !== 'all') {
                filtered = filtered.filter(s => s.status === currentFilter);
            }
            if (searchQuery) {
                const q = searchQuery.toLowerCase();
                filtered = filtered.filter(s =>
                    s.title.toLowerCase().includes(q) ||
                    (s.description && s.description.toLowerCase().includes(q))
                );
            }

            if (filtered.length === 0) {
                stepList.innerHTML = '<div class="empty-state"><p>No matching steps</p></div>';
                return;
            }

            stepList.innerHTML = filtered.map(s => {
                const ringClass = s.status !== 'not_started' ? s.status : '';
                const ringContent = s.status === 'completed' ? '&#10003;' : s.status === 'blocked' ? '!' : '';
                var card = '<div class="step-card ' + s.status + '" data-step-id="' + s.id + '" draggable="true" ondragstart="onDragStart(event,' + s.id + ')" ondragover="onDragOver(event)" ondrop="onDrop(event,' + s.id + ')" ondragend="onDragEnd(event)" onclick="toggleExpand(' + s.id + ', event)">' +
                    '<div class="step-drag"><div class="drag-row"><span class="drag-dot"></span><span class="drag-dot"></span></div><div class="drag-row"><span class="drag-dot"></span><span class="drag-dot"></span></div><div class="drag-row"><span class="drag-dot"></span><span class="drag-dot"></span></div></div>' +
                    '<div class="step-ring ' + ringClass + '" onclick="cycleStatus(' + s.id + ', \'' + s.status + '\', event)" title="Click to change status">' + ringContent + '</div>' +
                    '<div class="step-body">' +
                        '<div class="step-card-title">#' + s.id + ' ' + s.title + '</div>' +
                        '<div class="step-card-desc">' + (s.description || 'No description') + '</div>' +
                    '</div>' +
                    '<span class="step-priority ' + s.priority + '">' + s.priority + '</span>' +
                    '<div class="step-hover-actions">' +
                        '<button class="step-action-btn" onclick="updateStatus(' + s.id + ', \'in_progress\'); event.stopPropagation();" title="Start" aria-label="Start step ' + s.id + '">&#9654;</button>' +
                        '<button class="step-action-btn" onclick="updateStatus(' + s.id + ', \'completed\'); event.stopPropagation();" title="Done" aria-label="Complete step ' + s.id + '">&#10003;</button>' +
                        '<button class="step-action-btn" onclick="updateStatus(' + s.id + ', \'blocked\'); event.stopPropagation();" title="Block" aria-label="Block step ' + s.id + '">&#9888;</button>' +
                    '</div>' +
                '</div>';
                var expanded = '';
                if (expandedStepId === s.id) {
                    expanded = '<div class="step-expanded">' +
                        '<div class="step-expanded-header">' +
                            '<div class="step-ring ' + ringClass + '">' + ringContent + '</div>' +
                            '<div style="flex:1"><div class="step-card-title">#' + s.id + ' ' + s.title + '</div></div>' +
                            '<span class="step-priority ' + s.priority + '">' + s.priority + '</span>' +
                        '</div>' +
                        '<div class="step-expanded-grid">' +
                            '<div class="detail-section"><h4>Description</h4><p>' + (s.description || '<span class="detail-empty">No description</span>') + '</p></div>' +
                            '<div class="detail-section"><h4>Dependencies</h4>' +
                                (s.dependencies && s.dependencies.length > 0
                                    ? '<ul>' + s.dependencies.map(function(d) { return '<li>Step #' + d + '</li>'; }).join('') + '</ul>'
                                    : '<span class="detail-empty">None</span>') +
                            '</div>' +
                            '<div class="detail-section"><h4>Resources</h4>' +
                                (s.resources_needed && s.resources_needed.length > 0
                                    ? '<ul>' + s.resources_needed.map(function(r) { return '<li>' + r.name + (r.amount ? ' (' + r.amount + ')' : '') + '</li>'; }).join('') + '</ul>'
                                    : '<span class="detail-empty">None listed</span>') +
                            '</div>' +
                            '<div class="detail-section"><h4>Risks</h4>' +
                                (s.risks && s.risks.length > 0
                                    ? '<ul>' + s.risks.map(function(r) { return '<li>' + r.description + '</li>'; }).join('') + '</ul>'
                                    : '<span class="detail-empty">None identified</span>') +
                            '</div>' +
                        '</div>' +
                    '</div>';
                }
                return card + expanded;
            }).join('');
        }

        function setFilter(filter, el) {
            currentFilter = filter;
            document.querySelectorAll('.filter-pill').forEach(function(p) { p.classList.remove('active'); p.setAttribute('aria-selected', 'false'); });
            el.classList.add('active');
            el.setAttribute('aria-selected', 'true');
            if (window._allSteps) renderSteps(window._allSteps);
        }

        function cycleStatus(stepId, current, event) {
            event.stopPropagation();
            var cycle = { not_started: 'in_progress', in_progress: 'completed', completed: 'not_started', blocked: 'in_progress' };
            updateStatus(stepId, cycle[current] || 'in_progress');
        }

        function toggleExpand(stepId, event) {
            if (event.target.closest('.step-hover-actions') || event.target.closest('.step-ring') || event.target.closest('.step-drag')) return;
            if (expandedStepId === stepId) {
                expandedStepId = null;
            } else {
                expandedStepId = stepId;
            }
            if (window._allSteps) renderSteps(window._allSteps);
        }

        var draggedStepId = null;

        function onDragStart(e, stepId) {
            draggedStepId = stepId;
            e.dataTransfer.effectAllowed = 'move';
            e.target.style.opacity = '0.4';
        }

        function onDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            var card = e.target.closest('.step-card');
            if (card) {
                document.querySelectorAll('.step-card').forEach(function(c) { c.style.borderTopColor = ''; });
                card.style.borderTopColor = 'var(--accent)';
            }
        }

        function onDrop(e, targetStepId) {
            e.preventDefault();
            document.querySelectorAll('.step-card').forEach(function(c) { c.style.borderTopColor = ''; c.style.opacity = ''; });
            if (draggedStepId === null || draggedStepId === targetStepId) return;

            var targetIndex = window._allSteps.findIndex(function(s) { return s.id === targetStepId; });
            api('/api/plan/reorder', {
                method: 'PUT',
                body: JSON.stringify({ step_id: draggedStepId, new_position: targetIndex })
            }).then(function() {
                return api('/api/plan/save', { method: 'POST', body: JSON.stringify({ filename: currentPlan }) });
            }).then(function() {
                refreshPlanView();
            });
            draggedStepId = null;
        }

        function onDragEnd(e) {
            e.target.style.opacity = '';
            document.querySelectorAll('.step-card').forEach(function(c) { c.style.borderTopColor = ''; });
            draggedStepId = null;
        }

        function showExportMenu(e) {
            var menu = document.getElementById('exportMenu');
            var rect = e.target.getBoundingClientRect();
            menu.style.top = (rect.bottom + 4) + 'px';
            menu.style.left = rect.left + 'px';
            menu.classList.toggle('open');
            e.stopPropagation();
        }
        function closeExportMenu() { document.getElementById('exportMenu').classList.remove('open'); }
        document.addEventListener('click', closeExportMenu);

        // Search
        document.getElementById('searchInput').addEventListener('input', function(e) {
            searchQuery = e.target.value;
            if (window._allSteps) renderSteps(window._allSteps);
        });

        function showCreateModal() { document.getElementById('createModal').classList.add('active'); }
        function showAddStepModal() { document.getElementById('addStepModal').classList.add('active'); }
        function closeModal(id) { document.getElementById(id).classList.remove('active'); }

        async function createPlan(e) {
            e.preventDefault();
            const title = document.getElementById('newTitle').value;
            const description = document.getElementById('newDescription').value;
            const timeline = document.getElementById('newTimeline').value || 'TBD';
            const criteria = document.getElementById('newCriteria').value.split(',').map(s => s.trim()).filter(Boolean);
            const useAI = document.getElementById('useAI').value === 'yes';

            await api('/api/plan', {
                method: 'POST',
                body: JSON.stringify({ title, description, timeline, success_criteria: criteria, num_phases: useAI ? 0 : 5 })
            });

            if (useAI) {
                toast('Generating AI steps...');
                await api('/api/plan/generate-ai', { method: 'POST', body: JSON.stringify({ num_steps: 10 }) });
            }

            const filename = title.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '.json';
            await api('/api/plan/save', { method: 'POST', body: JSON.stringify({ filename }) });

            closeModal('createModal');
            toast('Plan created!');
            loadPlans();
            currentPlan = filename;
            refreshPlanView();
        }

        async function addStep(e) {
            e.preventDefault();
            await api('/api/plan/step', {
                method: 'POST',
                body: JSON.stringify({
                    title: document.getElementById('stepTitle').value,
                    description: document.getElementById('stepDescription').value,
                    priority: document.getElementById('stepPriority').value,
                    duration: document.getElementById('stepDuration').value
                })
            });
            await api('/api/plan/save', { method: 'POST', body: JSON.stringify({ filename: currentPlan }) });
            closeModal('addStepModal');
            toast('Step added');
            refreshPlanView();
        }

        async function generateAISteps() {
            toast('Generating AI steps...');
            const res = await api('/api/plan/generate-ai', { method: 'POST', body: JSON.stringify({ num_steps: 10 }) });
            if (res.status === 'success') {
                await api('/api/plan/save', { method: 'POST', body: JSON.stringify({ filename: currentPlan }) });
                toast('AI steps generated!');
                refreshPlanView();
            } else {
                toast(res.message || 'Failed', 'error');
            }
        }

        async function exportPDF() {
            const res = await api('/api/plan/export/pdf', { method: 'POST' });
            if (res.status === 'success') {
                window.open('/api/exports/' + res.filename, '_blank');
                toast('PDF exported');
            } else { toast(res.message, 'error'); }
        }

        async function exportHTML() {
            const res = await api('/api/plan/export/html', { method: 'POST' });
            if (res.status === 'success') {
                window.open('/api/exports/' + res.filename, '_blank');
                toast('HTML exported');
            } else { toast(res.message, 'error'); }
        }

        async function exportICal() {
            const res = await api('/api/plan/export/ical', { method: 'POST' });
            if (res.status === 'success') {
                window.open('/api/exports/' + res.filename, '_blank');
                toast('iCal exported');
            } else { toast(res.message, 'error'); }
        }

        var selectedStepIndex = -1;

        function showShortcuts() { document.getElementById('shortcutsOverlay').classList.add('active'); }
        function hideShortcuts() { document.getElementById('shortcutsOverlay').classList.remove('active'); }

        document.addEventListener('keydown', function(e) {
            var tag = document.activeElement.tagName;
            var inInput = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
            var modalOpen = document.querySelector('.modal.active') || document.querySelector('.shortcuts-overlay.active');

            if (e.key === 'Escape') {
                if (document.querySelector('.shortcuts-overlay.active')) { hideShortcuts(); return; }
                if (document.querySelector('.modal.active')) { document.querySelectorAll('.modal.active').forEach(function(m) { m.classList.remove('active'); }); return; }
                if (inInput) { document.activeElement.blur(); return; }
                if (expandedStepId !== null) { expandedStepId = null; if (window._allSteps) renderSteps(window._allSteps); return; }
                selectedStepIndex = -1;
                highlightSelected();
                return;
            }

            if (inInput || modalOpen) return;

            switch(e.key) {
                case 'n': showCreateModal(); e.preventDefault(); break;
                case 's': showAddStepModal(); e.preventDefault(); break;
                case '/': document.getElementById('searchInput').focus(); e.preventDefault(); break;
                case '?': showShortcuts(); e.preventDefault(); break;
                case 'j':
                    if (window._allSteps && window._allSteps.length > 0) {
                        selectedStepIndex = Math.min(selectedStepIndex + 1, window._allSteps.length - 1);
                        highlightSelected();
                    }
                    e.preventDefault();
                    break;
                case 'k':
                    if (window._allSteps) {
                        selectedStepIndex = Math.max(selectedStepIndex - 1, 0);
                        highlightSelected();
                    }
                    e.preventDefault();
                    break;
                case '1':
                    if (selectedStepIndex >= 0 && window._allSteps[selectedStepIndex]) {
                        updateStatus(window._allSteps[selectedStepIndex].id, 'in_progress');
                    }
                    break;
                case '2':
                    if (selectedStepIndex >= 0 && window._allSteps[selectedStepIndex]) {
                        updateStatus(window._allSteps[selectedStepIndex].id, 'completed');
                    }
                    break;
                case '3':
                    if (selectedStepIndex >= 0 && window._allSteps[selectedStepIndex]) {
                        updateStatus(window._allSteps[selectedStepIndex].id, 'blocked');
                    }
                    break;
            }
        });

        function highlightSelected() {
            document.querySelectorAll('.step-card').forEach(function(c, i) {
                c.style.outline = i === selectedStepIndex ? '2px solid var(--accent)' : '';
                c.style.outlineOffset = i === selectedStepIndex ? '2px' : '';
                if (i === selectedStepIndex) c.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            });
        }

        function fireConfetti(x, y, count) {
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

            var canvas = document.getElementById('confettiCanvas');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            var ctx = canvas.getContext('2d');
            var colors = ['#7c5cfc', '#9b7dff', '#34d399', '#fbbf24', '#f87171'];
            var particles = [];

            for (var i = 0; i < count; i++) {
                particles.push({
                    x: x, y: y,
                    vx: (Math.random() - 0.5) * 12,
                    vy: (Math.random() - 0.7) * 12,
                    size: Math.random() * 6 + 3,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    life: 1,
                    rotation: Math.random() * 360
                });
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                var alive = false;
                particles.forEach(function(p) {
                    if (p.life <= 0) return;
                    alive = true;
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vy += 0.3;
                    p.life -= 0.015;
                    p.rotation += p.vx * 2;
                    ctx.save();
                    ctx.translate(p.x, p.y);
                    ctx.rotate(p.rotation * Math.PI / 180);
                    ctx.globalAlpha = p.life;
                    ctx.fillStyle = p.color;
                    ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
                    ctx.restore();
                });
                if (alive) requestAnimationFrame(animate);
                else ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
            requestAnimationFrame(animate);
        }

        // Init
        loadPlans();
    </script>

    <div class="shortcuts-overlay" id="shortcutsOverlay" onclick="if(event.target===this)hideShortcuts()">
        <div class="shortcuts-card">
            <h2>Keyboard Shortcuts</h2>
            <div class="shortcut-row"><span>New plan</span><kbd>n</kbd></div>
            <div class="shortcut-row"><span>Add step</span><kbd>s</kbd></div>
            <div class="shortcut-row"><span>Search</span><kbd>/</kbd></div>
            <div class="shortcut-row"><span>Navigate steps</span><kbd>j</kbd> <kbd>k</kbd></div>
            <div class="shortcut-row"><span>Start selected</span><kbd>1</kbd></div>
            <div class="shortcut-row"><span>Complete selected</span><kbd>2</kbd></div>
            <div class="shortcut-row"><span>Block selected</span><kbd>3</kbd></div>
            <div class="shortcut-row"><span>Close / Deselect</span><kbd>Esc</kbd></div>
            <div class="shortcut-row"><span>Show shortcuts</span><kbd>?</kbd></div>
        </div>
    </div>
    <div class="shortcut-hint" onclick="showShortcuts()"><kbd>?</kbd> Shortcuts</div>
    <canvas id="confettiCanvas" style="position:fixed;inset:0;pointer-events:none;z-index:300;"></canvas>
</body>
</html>'''


if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) so it's accessible from mobile
    app.run(host='0.0.0.0', port=8080, debug=True)
