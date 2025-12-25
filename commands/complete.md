---
description: Mark steps as completed in your plan
---

# Mark Steps Complete

Help the user update step statuses in their backcasting plan:

1. **Identify the Step**: Ask which step they completed (by number or description).

2. **Update Status**: Use `backcast_update_step_status` with status "completed".

3. **Show Progress**: Display the updated progress percentage.

4. **Suggest Next**: Use `backcast_get_next_actions` to show what to work on next.

## Usage Examples

- "I finished step 3" → Mark step 3 as completed
- "Mark the research phase done" → Find and complete the research step
- "I'm done with all the setup tasks" → Mark multiple steps complete

## Available Statuses

- `completed` - Step is done
- `in_progress` - Currently working on it
- `blocked` - Cannot proceed (dependency issue)
- `skipped` - Decided not to do this step
