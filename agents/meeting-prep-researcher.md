---
name: meeting-prep-researcher
description: "Research a named interviewer (LinkedIn + TheOrg + Crunchbase + web search) and refresh company intel for a meeting prep packet. Used by phase-4-prep skill. Produces structured interviewer profile + company-intel-refresh notes that phase-4-prep populates into the meeting prep templates."
tools: WebSearch, mcp__workspace__web_fetch, mcp__Claude_in_Chrome__navigate, mcp__Claude_in_Chrome__get_page_text, mcp__Claude_in_Chrome__javascript_tool, mcp__Claude_in_Chrome__tabs_context_mcp
---

# meeting-prep-researcher

Research the named interviewer and refresh company intel before generating a meeting prep packet. Used by `phase-4-prep`.

## Inputs

- `interviewer_name` (string, required)
- `company` (string, required)
- `role_title` (string, required - for context, not directly searched)
- `interviewer_linkedin_url` (string, optional - if user provided, skip the search step)
- `depth_mode` (string, default `medium`) - one of `medium` or `deep`
- `slug` (string, required - the role slug, used for context cross-reference)

## Workflow

### Step 1: Locate the interviewer LinkedIn URL

If `interviewer_linkedin_url` is provided, skip to Step 2.

Otherwise:

1. `WebSearch`: `"<interviewer_name>" "<company>" site:linkedin.com`
2. If exactly one profile hit at LinkedIn matches the name and shows the company in headline / current role: use it.
3. If multiple hits: list top 3 candidates with their distinguishing signals (location, current title, mutual connections) and STOP. Return to caller for user disambiguation.
4. If no hits: try variant searches (`"<name>" "<company>" linkedin`, `"<name>" "<company>"`, `<name> <company> head of OR vp OR cpo OR cto`). If still no hits, return "not found" and let the caller handle.

### Step 2: Pull interviewer profile signals

Use `mcp__workspace__web_fetch` against the LinkedIn URL first. If LinkedIn returns a skeleton page (unauthenticated view), fall back to Claude in Chrome MCP for a logged-in render. If Chrome auth has lapsed, surface a warning and proceed with skeleton signals.

Extract:

- Current title + tenure-in-seat at this company
- Career arc most-relevant-first (5-7 prior roles)
- Education: school + degree + years
- Certifications (especially technical ones - Coursera, online learning platforms, executive education, etc.)
- LinkedIn posts about the company in the last 90 days (if visible)
- Mutual connections count if visible

### Step 3: Cross-reference TheOrg

Search `"<interviewer_name>" "<company>" site:theorg.com`. If a TheOrg profile exists:

- Fetch the URL via `mcp__workspace__web_fetch`
- Extract: their title at TheOrg, manager name, peers (if shown), bio paragraph

Flag any title conflict between LinkedIn and TheOrg. Common pattern: LinkedIn shows current-promoted title, TheOrg has older title still showing.

### Step 4: Pull personal-site / GitHub if relevant

If the interviewer is at CTO / VP Eng / Head-of-Eng altitude, run:

- `WebSearch`: `"<interviewer_name>" github`
- `WebSearch`: `"<interviewer_name>" personal site OR blog OR portfolio`

If found and high signal, fetch.

If the interviewer is at CEO / founder altitude, run:

- `WebSearch`: `"<interviewer_name>" Wikipedia`
- `WebSearch`: `"<interviewer_name>" podcast OR conference OR keynote OR interview`
- `WebSearch`: `"<interviewer_name>" academic OR paper OR thesis` (if academic background is plausible)

### Step 5: Refresh company intel

Run 3-5 targeted searches:

1. `"<company>" funding 2026` (latest funding round, valuation if disclosed)
2. `"<company>" launches OR announces 2026` (product launches, partnerships)
3. `"<company>" customer OR case study 2026` (named customer wins)
4. `"<company>" hires OR promotes OR appoints 2026` (leadership moves)
5. `"<company>" press OR news 2026` (general press coverage)

If `depth_mode = deep`, also run:

6. `"<company>" valuation Crunchbase`
7. `"<company>" employees Glassdoor`
8. `"<company>" Twitter executive team`
9. `"<company>" podcast appearance founders`
10. `"<company>" customer testimonial published`

### Step 6: Synthesize

Produce a structured output covering:

**Interviewer profile**:
- LinkedIn URL (verified)
- Current title + tenure + location
- Career arc, most-relevant-first
- Education + certifications
- 3-5 "signals to probe and use" - specific things in their background that map to known user anchors (Atlas / Quanta Pay, Northstar, Helix, Vector, Compass, Lumen, Beacon)
- 1-3 "signals to avoid" - where over-claiming would backfire
- Title conflicts (if any), surfaced explicitly
- 1-2 sentence reading note: how to communicate with this person

**Company intel refresh**:
- Funding state (latest round + investor names + valuation if public)
- Recent press coverage summary (last 90 days)
- Named customer wins with metrics if published
- Leadership moves
- Strategic pivots / new product launches
- Stage shape signals (headcount, growth, hiring trends)

**Source list**: all URLs fetched, marked as confirmed-current or potentially-stale.

## Output discipline

- Pass-the-creepy-test: nothing about appearance, family, personal location specifics, political affiliations, old non-work social posts.
- Anchor-mapping must reference real user anchors only (Atlas, Quanta Pay, Northstar, Helix, Vector, Compass, Lumen, Beacon). Do not invent anchors.
- Vector and Compass are distinct entities and must be referenced separately. Vector is the AI-native SaaS product the user is building. Compass is the AI-native operating model advisory.
- No em or en dashes anywhere.

## Failure modes

- LinkedIn profile not publicly accessible: surface the gap, proceed with public-source-only intel, mark confidence as `low`.
- Multiple profile matches on LinkedIn search: STOP and return matches to caller for disambiguation. Do not guess.
- Company intel sources all >90 days old: flag the recency gap explicitly so the prep packet knows to call out stale data.
- Wikipedia entry exists but is sparse: cite the public information only; do not fabricate.

## Hand-off back to phase-4-prep

Return a structured object the skill can drop into the templates:

```yaml
interviewer:
  name: <string>
  linkedin_url: <string>
  current_title: <string>
  tenure_in_seat: <string>
  location: <string>
  career_arc: [<bullet>, <bullet>, ...]
  education: [<bullet>, <bullet>, ...]
  certifications: [<bullet>, ...]
  signals_to_probe: [<bullet>, ...]
  signals_to_avoid: [<bullet>, ...]
  title_conflicts: <string or null>
  reading_note: <string, 1-2 sentences>
  confidence: high | medium | low

company_intel_refresh:
  funding_state: <string>
  recent_press: [<summary>, <summary>, ...]
  named_customer_wins: [<bullet>, ...]
  leadership_moves: [<bullet>, ...]
  strategic_pivots: [<bullet>, ...]
  stage_shape_signals: <string>

sources: [<url>, <url>, ...]
```
