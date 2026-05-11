---
name: daily-bump
description: Generate Day-5/7/10 follow-up bump messages for any pending roles. Triggers on "what bumps today", "Day-5 bumps", "follow-ups due", "/bump", "/bump X", or "what should I follow up on today". Reads the dashboard, finds roles in the bump window or past Day-10 final-action threshold, and drafts the appropriate bump message per role per follow-up.yaml templates.
---

# daily-bump

Generate follow-up bump messages for pending roles. Day-5 first touch, Day-7 second touch, Day-10 final.

## When to invoke

The user says: "what bumps today", "Day-5 bumps", "follow-ups due", "/bump", "/bump X", "what should I follow up on today", or first thing in the morning to pre-stage the day's bumps.

## Workflow

### Step 1: Scan the dashboard

Read the project's `dashboard.html` and parse the `ROLES = [...]` array. For each role:

- Skip roles with status `rejected`, `skipped`, or `replied`
- Skip roles with status `drafted` (not sent yet)
- For roles with `status: "pending"` and a `sendDate`, calculate days since send

### Step 2: Bucket by follow-up window

Per `${CLAUDE_PLUGIN_ROOT}/config/follow-up.yaml`:

- **Days 0-4 since send**: fresh window. Skip - do not bump.
- **Day 5**: first-touch bump (template `bump_templates.day_5_first_touch`)
- **Day 6-7**: still in bump window. Use Day-5 first-touch template.
- **Day 8-9**: skip the second-touch by default; the conventional rhythm is Day-5 then Day-10. Surface only if the user explicitly asks for a Day-7 or Day-9 second touch.
- **Day 10**: final-action template (`bump_templates.day_10_final`). User decision: send the final touch OR mark the role passive-skip.
- **Day 11+**: overdue. Surface as "should be closed out" - either fired final or marked passive-skip.

### Step 3: Generate per-role bumps

For each role in the bump window:

1. Read `outreach/{slug}/outreach.md` for the original message + contact name
2. Use the appropriate template from `follow-up.yaml.bump_templates`
3. Substitute `{first_name}`, `{role}`, `{self_first_name}` per the role's data
4. Apply `outreach-style.yaml` discipline: no em/en dashes, no trailing summaries, peer-to-peer tone, sign-off with first name only

### Step 4: Output

For each role with a bump due, output:

- Role identifier (company - role title)
- Days since send + window classification
- Original sendDate
- Drafted bump message (verbatim, char count)
- Recommended channel (same as original or escalation - e.g., if Day-5 Connect+Note unaccepted, consider Day-10 final on the same channel, or escalate to a peer of the original contact)
- Approval gate: "ready to send" / "edit" / "skip this bump"

For Day-10 final-action roles, also offer the **passive-skip** alternative:

```
{Company} - Day 10 final.
Option A: send final-touch message (drafted below)
Option B: mark passive-skip in dashboard, no message sent
```

### Step 5: User confirmation per bump

Each bump is a separate type-and-stop send (per Phase 3 safety rules). After the user says "send" for a particular bump, hand off to the same type-and-stop flow Phase 3 uses.

## Output format

Tight. Group by bucket. Lead with the count.

```
Today's bumps: 3 in Day-5 window, 1 at Day-10 final.

Day 5 (3):
  9fin (Moises): "Hi Moises, circling back on the note above re: VP Product..."
  NetApp (Pravjit): "Hi Pravjit, circling back..."
  Lyra Health (TBD): no contact identified at original send -> recommend skip bump, find contact first

Day 10 final (1):
  Spark Advisors: original send via InMail (1 credit burned), no reply.
  Option A: final touch via the same InMail thread
  Option B: mark passive-skip
```

## References

See `${CLAUDE_PLUGIN_ROOT}/config/follow-up.yaml` for the exact templates and window definitions. See `${CLAUDE_PLUGIN_ROOT}/skills/daily-bump/references/escalation-patterns.md` for second-touch escalation patterns (e.g., redirect-to-right-person, peer-of-original-contact).
