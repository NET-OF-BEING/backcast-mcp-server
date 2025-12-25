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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); min-height: 100vh; color: #e2e8f0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 1rem; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid #4c1d95; margin-bottom: 1.5rem; }
        h1 { color: #c4b5fd; font-size: 1.5rem; }
        .status-badge { background: #10b981; color: white; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; }
        .grid { display: grid; grid-template-columns: 300px 1fr; gap: 1.5rem; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        .sidebar { background: rgba(30, 27, 75, 0.8); border-radius: 12px; padding: 1rem; }
        .main { background: rgba(30, 27, 75, 0.6); border-radius: 12px; padding: 1.5rem; }
        h2 { color: #a5b4fc; font-size: 1rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
        .plan-list { list-style: none; }
        .plan-item { padding: 0.75rem; background: rgba(139, 92, 246, 0.2); border-radius: 8px; margin-bottom: 0.5rem; cursor: pointer; transition: all 0.2s; border: 1px solid transparent; }
        .plan-item:hover { border-color: #7c3aed; background: rgba(139, 92, 246, 0.3); }
        .plan-item.active { border-color: #a855f7; background: rgba(139, 92, 246, 0.4); }
        .btn { padding: 0.5rem 1rem; border-radius: 8px; border: none; cursor: pointer; font-weight: 500; transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.5rem; }
        .btn-primary { background: #7c3aed; color: white; }
        .btn-primary:hover { background: #6d28d9; }
        .btn-secondary { background: rgba(139, 92, 246, 0.3); color: #c4b5fd; border: 1px solid #7c3aed; }
        .btn-secondary:hover { background: rgba(139, 92, 246, 0.5); }
        .btn-success { background: #10b981; color: white; }
        .btn-success:hover { background: #059669; }
        .btn-group { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 1rem 0; }
        .progress-bar { background: #1e1b4b; border-radius: 999px; height: 8px; overflow: hidden; margin: 0.5rem 0; }
        .progress-fill { background: linear-gradient(90deg, #7c3aed, #a855f7); height: 100%; border-radius: 999px; transition: width 0.3s; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 0.75rem; margin: 1rem 0; }
        .stat-card { background: rgba(139, 92, 246, 0.15); border-radius: 8px; padding: 0.75rem; text-align: center; }
        .stat-value { font-size: 1.5rem; font-weight: bold; color: #a5b4fc; }
        .stat-label { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; }
        .step-list { max-height: 400px; overflow-y: auto; }
        .step-item { background: rgba(30, 27, 75, 0.8); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #6b7280; }
        .step-item.completed { border-left-color: #10b981; opacity: 0.7; }
        .step-item.in_progress { border-left-color: #3b82f6; }
        .step-item.blocked { border-left-color: #ef4444; }
        .step-header { display: flex; justify-content: space-between; align-items: start; gap: 0.5rem; }
        .step-title { font-weight: 500; flex: 1; }
        .step-badge { padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.65rem; font-weight: 500; }
        .badge-critical { background: #dc2626; color: white; }
        .badge-high { background: #f97316; color: white; }
        .badge-medium { background: #eab308; color: black; }
        .badge-low { background: #22c55e; color: white; }
        .step-desc { font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem; }
        .step-actions { margin-top: 0.5rem; display: flex; gap: 0.25rem; }
        .step-actions button { padding: 0.25rem 0.5rem; font-size: 0.7rem; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 100; align-items: center; justify-content: center; }
        .modal.active { display: flex; }
        .modal-content { background: #1e1b4b; border-radius: 12px; padding: 1.5rem; max-width: 500px; width: 90%; max-height: 80vh; overflow-y: auto; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
        .modal-close { background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.25rem; color: #a5b4fc; font-size: 0.85rem; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 0.5rem; border-radius: 6px; border: 1px solid #4c1d95; background: rgba(30, 27, 75, 0.8); color: #e2e8f0; }
        .form-group textarea { min-height: 80px; resize: vertical; }
        .toast { position: fixed; bottom: 1rem; right: 1rem; padding: 0.75rem 1rem; border-radius: 8px; color: white; font-weight: 500; z-index: 200; animation: slideIn 0.3s; }
        .toast-success { background: #10b981; }
        .toast-error { background: #ef4444; }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        .empty-state { text-align: center; padding: 2rem; color: #94a3b8; }
        .next-actions { background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
        .next-actions h3 { color: #10b981; font-size: 0.9rem; margin-bottom: 0.5rem; }
        .next-actions ul { list-style: none; font-size: 0.85rem; }
        .next-actions li { padding: 0.25rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Outcome Backcasting</h1>
            <span class="status-badge" id="connectionStatus">Connected</span>
        </header>

        <div class="grid">
            <aside class="sidebar">
                <h2>📁 Plans</h2>
                <button class="btn btn-primary" style="width:100%; margin-bottom:1rem;" onclick="showCreateModal()">+ New Plan</button>
                <ul class="plan-list" id="planList">
                    <li class="empty-state">Loading plans...</li>
                </ul>
            </aside>

            <main class="main">
                <div id="noPlanSelected" class="empty-state">
                    <h2>Select or create a plan</h2>
                    <p>Choose a plan from the sidebar or create a new one</p>
                </div>

                <div id="planDetails" style="display:none;">
                    <h2 id="planTitle">Plan Title</h2>
                    <p id="planDescription" style="color:#94a3b8; margin-bottom:1rem;"></p>

                    <div class="progress-bar">
                        <div class="progress-fill" id="progressBar" style="width:0%"></div>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card"><div class="stat-value" id="statPercent">0%</div><div class="stat-label">Complete</div></div>
                        <div class="stat-card"><div class="stat-value" id="statDone">0</div><div class="stat-label">Done</div></div>
                        <div class="stat-card"><div class="stat-value" id="statProgress">0</div><div class="stat-label">In Progress</div></div>
                        <div class="stat-card"><div class="stat-value" id="statBlocked">0</div><div class="stat-label">Blocked</div></div>
                        <div class="stat-card"><div class="stat-value" id="statTodo">0</div><div class="stat-label">To Do</div></div>
                    </div>

                    <div class="btn-group">
                        <button class="btn btn-primary" onclick="generateAISteps()">🤖 AI Generate Steps</button>
                        <button class="btn btn-secondary" onclick="exportPDF()">📄 PDF</button>
                        <button class="btn btn-secondary" onclick="exportHTML()">🌐 HTML</button>
                        <button class="btn btn-secondary" onclick="exportICal()">📅 iCal</button>
                        <button class="btn btn-success" onclick="showAddStepModal()">+ Add Step</button>
                    </div>

                    <div class="next-actions" id="nextActions" style="display:none;">
                        <h3>🎯 Next Actions</h3>
                        <ul id="nextActionsList"></ul>
                    </div>

                    <h2>📝 Steps</h2>
                    <div class="step-list" id="stepList"></div>
                </div>
            </main>
        </div>
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
                list.innerHTML = '<li class="empty-state">No plans yet</li>';
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

            document.getElementById('planTitle').textContent = overview.outcome.title;
            document.getElementById('planDescription').textContent = overview.outcome.description;

            const p = overview.progress;
            document.getElementById('progressBar').style.width = p.percent + '%';
            document.getElementById('statPercent').textContent = p.percent + '%';
            document.getElementById('statDone').textContent = p.completed;
            document.getElementById('statProgress').textContent = p.in_progress;
            document.getElementById('statBlocked').textContent = p.blocked;
            document.getElementById('statTodo').textContent = p.not_started;

            // Next actions
            if (nextActions.next_actions && nextActions.next_actions.length > 0) {
                document.getElementById('nextActions').style.display = 'block';
                document.getElementById('nextActionsList').innerHTML = nextActions.next_actions.slice(0,3).map(a =>
                    `<li><strong>${a.title}</strong> (${a.priority})</li>`
                ).join('');
            } else {
                document.getElementById('nextActions').style.display = 'none';
            }

            // Steps
            const stepList = document.getElementById('stepList');
            if (steps.steps && steps.steps.length > 0) {
                stepList.innerHTML = steps.steps.map(s => `
                    <div class="step-item ${s.status}">
                        <div class="step-header">
                            <span class="step-title">#${s.id} ${s.title}</span>
                            <span class="step-badge badge-${s.priority}">${s.priority}</span>
                        </div>
                        <div class="step-desc">${s.description || 'No description'}</div>
                        <div class="step-actions">
                            <button class="btn btn-secondary" onclick="updateStatus(${s.id}, 'in_progress')">▶️ Start</button>
                            <button class="btn btn-success" onclick="updateStatus(${s.id}, 'completed')">✓ Done</button>
                            <button class="btn btn-secondary" onclick="updateStatus(${s.id}, 'blocked')">🚫 Block</button>
                        </div>
                    </div>
                `).join('');
            } else {
                stepList.innerHTML = '<div class="empty-state">No steps yet. Click "AI Generate Steps" to create some!</div>';
            }
        }

        async function updateStatus(stepId, status) {
            await api('/api/plan/step/' + stepId + '/status', {
                method: 'PUT',
                body: JSON.stringify({ status })
            });
            await api('/api/plan/save', { method: 'POST', body: JSON.stringify({ filename: currentPlan }) });
            toast('Status updated');
            refreshPlanView();
        }

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

        // Init
        loadPlans();
    </script>
</body>
</html>'''


if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) so it's accessible from mobile
    app.run(host='0.0.0.0', port=8080, debug=True)
