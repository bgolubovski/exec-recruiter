---
name: dashboard-status
description: Read the current dashboard and surface today's actions, status counts, and follow-up windows. Triggers on "where do I stand", "today's actions", "dashboard status", "/dashboard", "what's the state", "status check", or first thing in the morning before the sweep. Lightweight read-only operation that summarizes the pipeline without changing anything.
---

# dashboard-status

Read the dashboard and surface today's state. Read-only.

## When to invoke

The user says: "where do I stand", "today's actions", "dashboard status", "/dashboard", "what's the state", "status check". Or as the opener for a daily working session.

## Workflow

### Step 1: Read the dashboard

Locate `dashboard.html` in the user's project folder. Parse the `ROLES = [...]` array.

### Step 2: Compute aggregates

Group roles by status:

- `pending` - sent, awaiting reply
- `drafted` - packet built, not sent
- `replied` - got a response
- `rejected` - turned down
- `skipped` - decided not to pursue

For `pending` roles, sub-bucket by follow-up window:

- Fresh (Days 0-4 since send)
- Bump window (Days 5-7)
- Day-10 final (Days 8-10)
- Overdue (Day 11+)

### Step 3: Compute today's actions

Today's actions list:

1. Roles in Day-5 to Day-7 bump window (from follow-up windows above)
2. Roles past Day-10 threshold awaiting close-out
3. Roles with `status: "drafted"` awaiting send (not always urgent, but list them)

### Step 4: Inbound signals

If the dashboard's "Inbound signals" section has new entries since the last status check, surface them:

- Profile views from people relevant to active roles
- Recruiter outreach received
- Rejection emails received

### Step 5: Output

Tight summary in chat. Format:

```
Pipeline state - {date}
Total roles: {total} | Pending: {pending} | Replied: {replied} | Rejected: {rejected} | Skipped: {skipped}

Today's actions:
- Day-5 bumps due (3): [list]
- Day-10 final-action (1): [list]
- Drafted, awaiting send (2): [list]

Inbound signals (last 24h):
- {signal 1}
- {signal 2}
```

## Discipline

Read-only. Do not modify the dashboard. Do not generate bump messages (that's `daily-bump`). Do not run a sweep (that's `phase-1-sweep`). Just surface state.

## When the dashboard is empty or absent

If there's no dashboard or it has zero roles, output:

```
No dashboard found. Run Phase 1 sweep to start sourcing roles, or scaffold an empty dashboard from the template at ${CLAUDE_PLUGIN_ROOT}/templates/dashboard.html.
```
