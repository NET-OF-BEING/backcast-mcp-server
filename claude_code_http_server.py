#!/home/panda/Documents/PythonScripts/OutcomeBackcasting/backcast_venv/bin/python3
"""
HTTP Server for Claude Code Integration

Allows mobile devices to send prompts to Claude Code and receive responses via HTTP.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)

# Store conversation history
conversation_history = []


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Claude Code HTTP Gateway',
        'version': '1.0'
    })


@app.route('/api/prompt', methods=['POST'])
def send_prompt():
    """Send a prompt to Claude Code and get response"""
    data = request.json

    if 'prompt' not in data:
        return jsonify({'status': 'error', 'message': 'Missing prompt field'}), 400

    prompt = data['prompt']

    # Add to conversation history
    conversation_history.append({
        'role': 'user',
        'content': prompt
    })

    try:
        # Use the Anthropic API directly
        import anthropic

        # Get API key from environment
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'ANTHROPIC_API_KEY not set in environment'
            }), 500

        client = anthropic.Anthropic(api_key=api_key)

        # Create message with conversation history
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8096,
            messages=conversation_history
        )

        # Extract response text
        response_text = response.content[0].text

        # Add assistant response to history
        conversation_history.append({
            'role': 'assistant',
            'content': response_text
        })

        return jsonify({
            'status': 'success',
            'response': response_text,
            'conversation_length': len(conversation_history)
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error calling Claude API: {str(e)}'
        }), 500


@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    """Get conversation history"""
    return jsonify({
        'status': 'success',
        'conversation': conversation_history,
        'length': len(conversation_history)
    })


@app.route('/api/conversation/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({
        'status': 'success',
        'message': 'Conversation cleared'
    })


@app.route('/api/conversation/export', methods=['GET'])
def export_conversation():
    """Export conversation as markdown"""
    markdown = "# Claude Conversation\n\n"

    for msg in conversation_history:
        role = msg['role'].title()
        content = msg['content']
        markdown += f"## {role}\n\n{content}\n\n---\n\n"

    return jsonify({
        'status': 'success',
        'markdown': markdown
    })


if __name__ == '__main__':
    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it in your ~/.bashrc or run:")
        print("export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    # Run on all interfaces (0.0.0.0) so it's accessible from mobile
    print("=" * 60)
    print("Claude Code HTTP Gateway")
    print("=" * 60)
    print("Server starting on http://0.0.0.0:8080")
    print("Access from mobile at: http://10.139.148.158:8080")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8080, debug=True)
