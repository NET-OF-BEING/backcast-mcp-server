#!/usr/bin/env python3
"""
Create an example backcasting plan to demonstrate the system
"""

from backcast_engine import (
    BackcastEngine, Outcome, Step, Resource, Risk,
    StepType, StepStatus, Priority, BackcastPlan
)

def create_example_plan():
    """Create a comprehensive example plan"""

    engine = BackcastEngine()

    # Define the outcome
    outcome = Outcome(
        title="Launch AI-Powered Personal Assistant Product",
        description="Build and launch a SaaS product that provides AI-powered personal "
                   "assistance for productivity and task management. Target 1000 paying "
                   "users in first 6 months with $50/month subscription.",
        success_criteria=[
            "1000+ paying subscribers at $50/month",
            "Product stability: 99.5% uptime",
            "Average user rating of 4.5+ stars",
            "Core features: task management, calendar integration, AI suggestions",
            "Payment processing fully integrated",
            "Customer support system operational"
        ],
        constraints=[
            "Budget: $150,000 total",
            "Team: 3 full-time developers + 1 designer",
            "Must comply with GDPR and data privacy regulations",
            "No external funding (bootstrap)",
            "Must be profitable by month 9"
        ],
        timeline="9 months"
    )

    # Create plan
    plan = BackcastPlan(outcome=outcome, steps=[])

    # Create steps (working from present to future for easier definition)
    steps_data = [
        # Phase 1: Foundation (Month 1)
        {
            "id": 1,
            "title": "Project Kickoff and Planning",
            "description": "Assemble team, finalize architecture, set up development environment",
            "type": StepType.MILESTONE,
            "priority": Priority.CRITICAL,
            "status": StepStatus.COMPLETED,
            "duration": "2 weeks",
            "dependencies": [],
            "criteria": ["Team assembled", "Tech stack finalized", "Project roadmap created"],
            "resources": [
                Resource("Project Manager", "person", "1 person"),
                Resource("Development setup", "time", "1 week")
            ],
            "risks": []
        },
        {
            "id": 2,
            "title": "Design User Experience and Workflows",
            "description": "Create wireframes, user flows, and initial design system",
            "type": StepType.ACTION,
            "priority": Priority.HIGH,
            "status": StepStatus.COMPLETED,
            "duration": "3 weeks",
            "dependencies": [1],
            "criteria": ["Wireframes approved", "User flows documented", "Design system v1"],
            "resources": [
                Resource("UX Designer", "person", "1 person full-time"),
                Resource("Figma", "tool", "Professional plan")
            ],
            "risks": [
                Risk(
                    "Design requires multiple iterations",
                    "medium",
                    "medium",
                    "Get early feedback from potential users, use existing design patterns"
                )
            ]
        },

        # Phase 2: Core Development (Months 2-4)
        {
            "id": 3,
            "title": "Build Backend Infrastructure",
            "description": "Set up database, API endpoints, authentication system, cloud infrastructure",
            "type": StepType.ACTION,
            "priority": Priority.CRITICAL,
            "status": StepStatus.IN_PROGRESS,
            "duration": "6 weeks",
            "dependencies": [1, 2],
            "criteria": ["API documentation complete", "Auth system tested", "Database schema finalized"],
            "resources": [
                Resource("Backend Developer", "person", "2 developers"),
                Resource("AWS/Cloud hosting", "money", "$2000/month"),
                Resource("PostgreSQL", "tool", "Database")
            ],
            "risks": [
                Risk(
                    "Scalability issues with initial architecture",
                    "medium",
                    "high",
                    "Design for horizontal scaling from day one, load testing"
                )
            ]
        },
        {
            "id": 4,
            "title": "Integrate AI/LLM Capabilities",
            "description": "Connect to AI APIs (OpenAI/Anthropic), build prompt engineering system",
            "type": StepType.ACTION,
            "priority": Priority.CRITICAL,
            "status": StepStatus.NOT_STARTED,
            "duration": "4 weeks",
            "dependencies": [3],
            "criteria": ["AI responses working", "Context management system", "Cost optimization implemented"],
            "resources": [
                Resource("AI/ML Engineer", "person", "1 person"),
                Resource("API Credits", "money", "$5000 initial"),
                Resource("LLM expertise", "skill", "Prompt engineering")
            ],
            "risks": [
                Risk(
                    "AI API costs exceed budget",
                    "high",
                    "high",
                    "Implement caching, rate limiting, and usage monitoring from start"
                ),
                Risk(
                    "AI response quality inconsistent",
                    "medium",
                    "high",
                    "Extensive testing, fallback responses, prompt refinement process"
                )
            ]
        },
        {
            "id": 5,
            "title": "Build Frontend Application",
            "description": "Develop web application with React, implement UI components",
            "type": StepType.ACTION,
            "priority": Priority.HIGH,
            "status": StepStatus.NOT_STARTED,
            "duration": "8 weeks",
            "dependencies": [2, 3],
            "criteria": ["All core screens implemented", "Responsive design working", "Accessibility standards met"],
            "resources": [
                Resource("Frontend Developer", "person", "2 developers"),
                Resource("React/TypeScript", "tool", "Framework"),
            ],
            "risks": []
        },

        # Phase 3: Integration (Month 5)
        {
            "id": 6,
            "title": "Implement Calendar and Task Integrations",
            "description": "Connect to Google Calendar, Outlook, Todoist, etc.",
            "type": StepType.ACTION,
            "priority": Priority.HIGH,
            "status": StepStatus.NOT_STARTED,
            "duration": "4 weeks",
            "dependencies": [4, 5],
            "criteria": ["At least 3 integrations working", "OAuth flows tested", "Sync logic reliable"],
            "resources": [
                Resource("Integration Developer", "person", "1 developer"),
                Resource("API access", "tool", "Third-party APIs")
            ],
            "risks": [
                Risk(
                    "Third-party API changes break integration",
                    "medium",
                    "medium",
                    "Build abstraction layer, monitor API changelog, have fallback options"
                )
            ]
        },
        {
            "id": 7,
            "title": "Integrate Payment Processing",
            "description": "Set up Stripe, implement subscription management, billing system",
            "type": StepType.ACTION,
            "priority": Priority.CRITICAL,
            "status": StepStatus.NOT_STARTED,
            "duration": "3 weeks",
            "dependencies": [3],
            "criteria": ["Payment flow tested", "Subscription tiers working", "Invoice generation automated"],
            "resources": [
                Resource("Stripe integration", "tool", "Payment gateway"),
                Resource("Backend Developer", "person", "1 developer")
            ],
            "risks": [
                Risk(
                    "Payment compliance issues (PCI-DSS)",
                    "low",
                    "high",
                    "Use Stripe Elements (hosted), never store card data"
                )
            ]
        },

        # Phase 4: Testing & Refinement (Month 6)
        {
            "id": 8,
            "title": "Alpha Testing with Internal Team",
            "description": "Extensive internal testing, bug fixing, performance optimization",
            "type": StepType.MILESTONE,
            "priority": Priority.HIGH,
            "status": StepStatus.NOT_STARTED,
            "duration": "2 weeks",
            "dependencies": [5, 6, 7],
            "criteria": ["All critical bugs fixed", "Performance benchmarks met", "Security audit passed"],
            "resources": [
                Resource("QA Tester", "person", "1 person"),
                Resource("Testing time", "time", "2 weeks full team")
            ],
            "risks": []
        },
        {
            "id": 9,
            "title": "Conduct Security Audit",
            "description": "Professional security review, penetration testing, fix vulnerabilities",
            "type": StepType.RISK_MITIGATION,
            "priority": Priority.CRITICAL,
            "status": StepStatus.NOT_STARTED,
            "duration": "2 weeks",
            "dependencies": [8],
            "criteria": ["No high/critical vulnerabilities", "Audit report received", "All issues resolved"],
            "resources": [
                Resource("Security Auditor", "person", "External contractor"),
                Resource("Security audit", "money", "$10,000")
            ],
            "risks": [
                Risk(
                    "Major vulnerabilities found requiring architecture changes",
                    "low",
                    "high",
                    "Follow security best practices from day one, regular code reviews"
                )
            ]
        },
        {
            "id": 10,
            "title": "Beta Testing with 50 Users",
            "description": "Invite beta testers, gather feedback, iterate on features",
            "type": StepType.MILESTONE,
            "priority": Priority.HIGH,
            "status": StepStatus.NOT_STARTED,
            "duration": "4 weeks",
            "dependencies": [9],
            "criteria": ["50 active beta users", "Feedback collected and analyzed", "Top issues addressed"],
            "resources": [
                Resource("Beta testers", "person", "50 external users"),
                Resource("Customer support", "person", "1 person"),
                Resource("Feedback tools", "tool", "Survey/analytics software")
            ],
            "risks": []
        },

        # Phase 5: Launch Preparation (Month 7)
        {
            "id": 11,
            "title": "Create Marketing Website and Materials",
            "description": "Landing page, documentation, help center, video demos",
            "type": StepType.ACTION,
            "priority": Priority.HIGH,
            "status": StepStatus.NOT_STARTED,
            "duration": "3 weeks",
            "dependencies": [10],
            "criteria": ["Website live", "Documentation complete", "Demo videos published"],
            "resources": [
                Resource("Marketing specialist", "person", "1 person"),
                Resource("Video production", "money", "$5,000"),
                Resource("Copywriter", "person", "Contractor")
            ],
            "risks": []
        },
        {
            "id": 12,
            "title": "Set Up Customer Support System",
            "description": "Help desk software, chatbot, documentation, support workflows",
            "type": StepType.ACTION,
            "priority": Priority.MEDIUM,
            "status": StepStatus.NOT_STARTED,
            "duration": "2 weeks",
            "dependencies": [10],
            "criteria": ["Support portal live", "Chatbot responding", "Team trained on support"],
            "resources": [
                Resource("Help desk software", "tool", "Intercom/Zendesk"),
                Resource("Support agent", "person", "1 person part-time")
            ],
            "risks": []
        },
        {
            "id": 13,
            "title": "Prepare Launch Campaign",
            "description": "Social media, Product Hunt, email outreach, PR strategy",
            "type": StepType.ACTION,
            "priority": Priority.MEDIUM,
            "status": StepStatus.NOT_STARTED,
            "duration": "3 weeks",
            "dependencies": [11],
            "criteria": ["Product Hunt launch scheduled", "Press kit ready", "Email list of 500+"],
            "resources": [
                Resource("Marketing budget", "money", "$15,000"),
                Resource("PR consultant", "person", "Contractor")
            ],
            "risks": [
                Risk(
                    "Launch doesn't get traction",
                    "medium",
                    "high",
                    "Build email list pre-launch, engage communities, create buzz early"
                )
            ]
        },

        # Phase 6: Launch (Month 8)
        {
            "id": 14,
            "title": "Public Launch",
            "description": "Official launch, monitor systems, respond to feedback in real-time",
            "type": StepType.MILESTONE,
            "priority": Priority.CRITICAL,
            "status": StepStatus.NOT_STARTED,
            "duration": "1 week",
            "dependencies": [11, 12, 13],
            "criteria": ["Product publicly available", "Payment processing live", "Support responding < 2 hours"],
            "resources": [
                Resource("Full team", "person", "All hands for launch week"),
                Resource("Monitoring tools", "tool", "Datadog/New Relic")
            ],
            "risks": [
                Risk(
                    "System crashes under load",
                    "medium",
                    "high",
                    "Load testing beforehand, auto-scaling enabled, incident response plan"
                )
            ]
        },

        # Phase 7: Growth (Month 9)
        {
            "id": 15,
            "title": "Growth and Iteration Phase",
            "description": "Marketing campaigns, feature iterations based on user feedback, optimize conversion",
            "type": StepType.ACTION,
            "priority": Priority.HIGH,
            "status": StepStatus.NOT_STARTED,
            "duration": "Ongoing",
            "dependencies": [14],
            "criteria": ["Active marketing campaigns", "Weekly feature updates", "Conversion funnel optimized"],
            "resources": [
                Resource("Marketing spend", "money", "$20,000/month"),
                Resource("Growth team", "person", "2 people")
            ],
            "risks": []
        },
        {
            "id": 16,
            "title": "Achieve 1000 Paying Subscribers",
            "description": "Final outcome: 1000+ subscribers at $50/month, sustainable business",
            "type": StepType.MILESTONE,
            "priority": Priority.CRITICAL,
            "status": StepStatus.NOT_STARTED,
            "duration": "Target: End of month 9",
            "dependencies": [15],
            "criteria": [
                "1000+ paying subscribers",
                "Monthly recurring revenue: $50,000",
                "Churn rate < 5%",
                "Customer satisfaction > 4.5/5"
            ],
            "resources": [],
            "risks": [
                Risk(
                    "Growth slower than expected",
                    "medium",
                    "high",
                    "Multiple marketing channels, referral program, aggressive content marketing"
                )
            ]
        }
    ]

    # Create Step objects
    for step_data in steps_data:
        step = Step(
            id=step_data["id"],
            title=step_data["title"],
            description=step_data["description"],
            type=step_data["type"],
            priority=step_data["priority"],
            status=step_data["status"],
            estimated_duration=step_data["duration"],
            resources_needed=step_data["resources"],
            dependencies=step_data["dependencies"],
            success_criteria=step_data["criteria"],
            risks=step_data["risks"]
        )
        plan.steps.append(step)

    # Save the plan
    filename = "example_ai_assistant_launch.json"
    filepath = engine.save_plan(plan, filename)

    print(f"✓ Example plan created successfully!")
    print(f"  Title: {outcome.title}")
    print(f"  Steps: {len(plan.steps)}")
    print(f"  Timeline: {outcome.timeline}")
    print(f"  Saved to: {filepath}")
    print(f"\nTo view this plan, run: ./run_backcast.sh")
    print(f"Then choose option 2 (Load existing plan) and select '{filename}'")

if __name__ == '__main__':
    create_example_plan()
