#!/usr/bin/env python3
"""
Voice-Enabled Backcasting Assistant
Speak to manage your backcasting plans using natural voice commands.

Commands:
- "list plans" / "show plans" - List all saved plans
- "load [plan name]" - Load a specific plan
- "what's next" / "next action" - Get your next actionable steps
- "progress" / "status" - Check current plan progress
- "mark complete [step number]" - Mark a step as completed
- "start step [step number]" - Mark a step as in progress
- "create plan [name]" - Create a new plan
- "analyze" - Get plan analysis and suggestions
- "help" - Show available commands

Press Ctrl+C to exit.
"""

import os
import sys
import re

# Add backcasting engine to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import speech_recognition as sr
from anthropic import Anthropic
from backcast_engine import BackcastEngine, StepStatus, Outcome


def main():
    # Initialize
    recognizer = sr.Recognizer()
    engine = BackcastEngine()

    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # State
    current_plan = None
    current_plan_name = None
    conversation_history = []

    # System prompt for Claude to understand backcasting commands
    system_prompt = """You are a helpful voice assistant for the Outcome Backcasting Engine.
You help users manage their strategic plans by interpreting their voice commands.

When users speak, extract their intent and respond helpfully. Keep responses concise (1-3 sentences) since they will be read aloud.

Available commands you can help with:
- List plans
- Load a plan
- Get next actions
- Check progress
- Mark steps complete/in progress
- Create new plans
- Analyze plans

If the user's request is unclear, ask a clarifying question.
Always be encouraging about their progress and goals."""

    print("=" * 60)
    print("🎯 Voice Backcasting Assistant")
    print("=" * 60)
    print("Speak commands like:")
    print("  • 'List my plans'")
    print("  • 'Load [plan name]'")
    print("  • 'What should I work on next?'")
    print("  • 'Mark step 3 complete'")
    print("  • 'What's my progress?'")
    print("=" * 60)
    print("\nListening... (Ctrl+C to exit)\n")

    try:
        while True:
            # Listen for audio
            with sr.Microphone() as source:
                print("🎤 Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                recognizer.pause_threshold = 1.5
                recognizer.energy_threshold = 300

                try:
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)
                    print("Processing...")
                except sr.WaitTimeoutError:
                    print("No speech detected. Try again.")
                    continue

            # Convert speech to text
            try:
                text = recognizer.recognize_google(audio)
                print(f"\n📢 You: {text}")

                # Process command locally first
                response = process_command(text.lower(), engine, current_plan, current_plan_name)

                if response:
                    # Update state if command changed plan
                    if response.get('plan'):
                        current_plan = response['plan']
                    if response.get('plan_name'):
                        current_plan_name = response['plan_name']

                    print(f"\n🤖 Assistant: {response['message']}")
                else:
                    # Use Claude for complex/unclear commands
                    context = f"""Current state:
- Active plan: {current_plan_name or 'None'}
- Available plans: {', '.join(engine.list_plans()) or 'None'}
"""
                    if current_plan:
                        progress = engine.calculate_progress(current_plan)
                        context += f"- Progress: {progress['percent']}% ({progress['completed']}/{progress['total']} steps)"

                    conversation_history.append({
                        "role": "user",
                        "content": f"[Context: {context}]\n\nUser said: {text}"
                    })

                    claude_response = client.messages.create(
                        model="claude-sonnet-4-5-20250929",
                        max_tokens=200,
                        system=system_prompt,
                        messages=conversation_history
                    )

                    assistant_message = claude_response.content[0].text
                    print(f"\n🤖 Assistant: {assistant_message}")

                    conversation_history.append({
                        "role": "assistant",
                        "content": assistant_message
                    })

            except sr.UnknownValueError:
                print("Could not understand audio. Please try again.")
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
            except Exception as e:
                print(f"Error: {e}")

    except KeyboardInterrupt:
        print("\n\nGoodbye! Keep working towards your goals! 🎯")
        sys.exit(0)


def process_command(text, engine, current_plan, current_plan_name):
    """Process voice commands and return response"""

    # List plans
    if any(phrase in text for phrase in ['list plan', 'show plan', 'my plan', 'what plan']):
        plans = engine.list_plans()
        if plans:
            plan_names = [p.replace('.json', '') for p in plans]
            return {'message': f"You have {len(plans)} plans: {', '.join(plan_names)}"}
        return {'message': "You don't have any plans yet. Say 'create plan' to make one."}

    # Load plan
    if 'load' in text and 'plan' in text:
        plans = engine.list_plans()
        # Try to find matching plan
        for plan_file in plans:
            plan_name = plan_file.replace('.json', '').lower()
            if plan_name in text or any(word in plan_name for word in text.split()):
                loaded = engine.load_plan(plan_file)
                return {
                    'message': f"Loaded plan: {loaded.outcome.title}",
                    'plan': loaded,
                    'plan_name': plan_file
                }
        return {'message': f"Couldn't find that plan. Available: {', '.join(p.replace('.json','') for p in plans)}"}

    # Next actions
    if any(phrase in text for phrase in ['next', 'what should', 'to do', 'action']):
        if not current_plan:
            return {'message': "No plan loaded. Say 'load' followed by a plan name."}

        next_actions = engine.get_next_actions(current_plan)
        if next_actions:
            top_actions = next_actions[:3]
            action_list = ". ".join([f"{a.title}" for a in top_actions])
            return {'message': f"Your next actions are: {action_list}"}
        return {'message': "No actions available. All steps may be completed or blocked."}

    # Progress
    if any(phrase in text for phrase in ['progress', 'status', 'how am i', 'percent']):
        if not current_plan:
            return {'message': "No plan loaded. Say 'load' followed by a plan name."}

        progress = engine.calculate_progress(current_plan)
        return {
            'message': f"You're {progress['percent']}% complete. "
                      f"{progress['completed']} done, {progress['in_progress']} in progress, "
                      f"{progress['not_started']} to do."
        }

    # Mark complete
    if 'complete' in text or 'done' in text or 'finish' in text:
        if not current_plan:
            return {'message': "No plan loaded."}

        # Extract step number
        numbers = re.findall(r'\d+', text)
        if numbers:
            step_id = int(numbers[0])
            try:
                updated = engine.update_step(current_plan, step_id, status=StepStatus.COMPLETED)
                step = next((s for s in updated.steps if s.id == step_id), None)
                if step:
                    engine.save_plan(updated, current_plan_name)
                    progress = engine.calculate_progress(updated)
                    return {
                        'message': f"Marked step {step_id} as complete! You're now {progress['percent']}% done.",
                        'plan': updated
                    }
            except:
                pass
        return {'message': "Say 'mark step [number] complete' to mark a specific step."}

    # Start step
    if 'start' in text or 'begin' in text or 'working on' in text:
        if not current_plan:
            return {'message': "No plan loaded."}

        numbers = re.findall(r'\d+', text)
        if numbers:
            step_id = int(numbers[0])
            try:
                updated = engine.update_step(current_plan, step_id, status=StepStatus.IN_PROGRESS)
                step = next((s for s in updated.steps if s.id == step_id), None)
                if step:
                    engine.save_plan(updated, current_plan_name)
                    return {
                        'message': f"Started step {step_id}: {step.title}. Good luck!",
                        'plan': updated
                    }
            except:
                pass
        return {'message': "Say 'start step [number]' to begin working on a step."}

    # Analyze
    if 'analyze' in text or 'analysis' in text or 'suggest' in text:
        if not current_plan:
            return {'message': "No plan loaded."}

        from backcast_engine import BackcastAnalyzer
        analyzer = BackcastAnalyzer()
        suggestions = analyzer.suggest_optimizations(current_plan)
        if suggestions:
            return {'message': suggestions[0]}
        return {'message': "Your plan looks well-structured!"}

    # Help
    if 'help' in text or 'command' in text:
        return {
            'message': "You can say: list plans, load plan, what's next, "
                      "progress, mark complete, start step, or analyze."
        }

    # No match - return None to use Claude
    return None


if __name__ == "__main__":
    main()
