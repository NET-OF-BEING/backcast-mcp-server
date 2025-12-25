---
description: Export your plan to PDF, iCal, or HTML
---

# Export Backcasting Plan

Help the user export their plan to different formats:

## Available Formats

1. **PDF** - Professional report with progress tables
   - Use `backcast_export_pdf` tool
   - Great for printing or sharing with stakeholders

2. **iCal** - Calendar format (.ics)
   - Use `backcast_export_ical` tool
   - Import into Google Calendar, Outlook, Apple Calendar
   - Steps become scheduled events based on duration

3. **HTML** - Styled web report
   - Use `backcast_export_html` tool
   - Beautiful visual report viewable in any browser
   - Includes progress charts and step details

## Workflow

1. Ensure a plan is loaded (use `backcast_load_plan` if needed)
2. Ask user which format they want
3. Call the appropriate export tool
4. Provide the file path so they can access it

## Example

User: "Export my startup plan to PDF"

You: Load the plan, call `backcast_export_pdf`, and tell them where the file is saved.
