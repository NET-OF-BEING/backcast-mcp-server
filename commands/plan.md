---
description: Create a new outcome backcasting plan
---

# Create Backcasting Plan

Help the user create a strategic backcasting plan by:

1. **Understand the Outcome**: Ask the user to describe their desired future outcome in detail. What does success look like? What are the success criteria?

2. **Define Constraints**: Identify timeline, budget, resource limitations, and any other constraints.

3. **Generate Steps**: Use the `backcast_create_plan` MCP tool to create the plan, then use `backcast_generate_ai_steps` to generate AI-powered steps that work backwards from the outcome to present actions.

4. **Review & Refine**: Show the user the generated steps and ask if any need adjustment.

5. **Save the Plan**: Use `backcast_save_plan` to save the plan for future reference.

## Example Interaction

User: "I want to launch a SaaS product in 6 months"

You should:
- Ask clarifying questions about the product, target market, success metrics
- Create the plan with appropriate success criteria
- Generate 10-15 AI-powered steps
- Present the plan and offer to refine it
