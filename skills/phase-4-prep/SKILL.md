---
name: phase-4-prep
description: "Build a meeting / interview prep packet for a booked conversation on a specific role. Triggers on \"prep me for X\", \"build prep packet for X\", \"interview prep X\", \"/prep <slug> <interviewer-name>\", \"screening call prep\", \"panel prep\", \"final round prep\". Pulls role context from the dashboard, researches the named interviewer (LinkedIn, TheOrg, Crunchbase, web), refreshes company intel, generates the scope-disambiguation question, first-90-days narrative (with branches if scope is ambiguous), questions to ask, one-line answers to likely questions back, comp posture, friction flags, and a wrap-up signal checklist. Saves three artifacts: full markdown, interactive HTML, and a one-page scannable card. Supports rounds screen / working-session / panel / final / exec / reference-check-prep. User-invoked only, never auto-fires."
---

# phase-4-prep

Build a meeting / interview prep packet for a booked conversation on a specific role. Pulls role context from the dashboard, researches the interviewer, refreshes company intel, generates the scope-disambiguation question, first-90-days narrative (with branches if scope is ambiguous), questions to ask, one-line answers to likely questions back, comp posture, friction flags, and a wrap-up signal checklist. Saves three artifacts: full markdown, interactive HTML, and a one-page scannable card.

## When to invoke

The user says: "prep me for X", "build prep packet for X", "interview prep X", "/prep X", "/prep <slug> <interviewer-name>", or "prep for the <name> call". Also valid: "screening call prep <slug>", "panel prep <slug>", "final round prep <slug>".

Phase 4 fires user-invoked only. Never auto-fires from a dashboard signal (booking detected, accept signal, etc.).

## Inputs

- `slug` - the role slug from the dashboard (required)
- `interviewer_name` - primary interviewer (required; if missing, ask)
- `interviewer_linkedin_url` - if user has it (saves a research step). If missing, the skill searches by name + company.
- `round` - one of: `screen` (recruiter / hiring-manager intro), `working-session`, `panel`, `final`, `exec`, `reference-check-prep`. Default: `screen`.
- `meeting_when` - date / time / day
- `meeting_format` - 30-min video, 60-min on-site, panel, etc.
- `--deep` flag (optional) - triggers maximum-depth company intel research

If the user names a meeting but the role is not in the dashboard, refuse and ask the user to add it via phase-1-sweep or phase-2-packet first. Do not generate prep against a non-existent role context.

## Workflow

### Step 1: Read role context

Read `dashboard.html` and parse the `ROLES` array. Find the entry by `slug`. Extract:

- `role`, `company`, `location`, `comp`, `score`
- `jdUrl`, ATS URL if present in `note`
- Pattern-match anchors used in the original packet (from `outreach/{slug}/jd.md`)
- Friction flags already identified
- Channels in play, sendDate, status
- Existing prior outreach (from `outreach/{slug}/outreach.md` and any `SEND-*.txt` files)

If `outreach/{slug}/jd.md` does not exist, refuse and ask the user to run phase-2-packet first.

### Step 2: Research the interviewer

Delegate to the `meeting-prep-researcher` agent. The agent runs:

1. If `interviewer_linkedin_url` not provided: web search `"<interviewer_name>" "<company>" site:linkedin.com` to find the canonical profile. If multiple profiles match, list and ask user to confirm.
2. Once URL is found: pull profile signals via Claude in Chrome MCP or `mcp__workspace__web_fetch` against the LinkedIn profile + public CV pages (TheOrg, Crunchbase, personal site, GitHub).
3. Cross-reference for title conflicts (LinkedIn vs TheOrg vs company website). Flag conflicts explicitly. The Sam Carter case from the canonical example showed VP Product on TheOrg + LinkedIn but Head of Product in older bios; the conflict matters for scope disambiguation.
4. Pull career arc (most-relevant-first), education, certifications, mutuals if visible.
5. Cluster the signals worth probing in the call (where their experience overlaps the user's anchors) and the signals to avoid (where overclaiming would backfire).

### Step 3: Refresh company intel

Default depth: more than light. Run 3-5 targeted web searches covering:

1. Funding history beyond what was captured at Phase-2 packet build (any new round, valuation change, lead investors)
2. Recent press coverage (last 90 days)
3. Customer wins or notable case studies (look for named customer + outcome metrics)
4. Leadership moves (CEO, CTO, CPO, head-of changes; new VP hires)
5. Strategic pivots / new product launches / partnerships

If `--deep` flag is set: extend to crunchbase profile, TheOrg org chart, Twitter/X executive activity, podcast appearances, conference speaking slots, Glassdoor signal, employee LinkedIn growth signal.

### Step 4: Generate the scope-disambiguation question

The scope-disambiguation question is the highest-leverage question on the call. It differs by round and interviewer altitude:

- **Recruiter screen**: probe comp band, work-auth, timeline, role-rank in pipeline ("how many people are you in conversation with?")
- **Hiring manager 1st call**: probe scope (above me, beside me, backfilling?), reporting line, team-shape, why-this-role-exists. The incumbent-product-leader-already-exists archetype.
- **Working session / 2nd round**: probe specific product trade-offs, customer reality, what good looks like in 90 days
- **Panel**: probe coverage map - which panelist owns which dimension and what they're testing
- **Final / CEO / founder**: probe commercial-model strategy, board-readiness, fundraising posture, what would make this hire a regret in 12 months
- **Reference-check prep**: not a question to ask the interviewer; instead surface the reference list curation and per-referee talking points

Always generate ONE primary scope-disambiguation question with a clean phrasing, and 1-2 backup variants in case the primary doesn't get answered cleanly.

### Step 5: Generate first-90-days narrative

If scope is unambiguous: one narrative.

If scope is ambiguous (typical for first hiring-manager calls): three branched narratives, one per plausible scope. Each narrative is 90-120 words, follows the same structure (customer-first, no panic moves, operating rhythm by day 90, explicit respect for incumbent product team).

Don't fabricate first-90-day details. Anchor every move to a real pattern the user has executed before (Northstar multi-product launch cadence, Helix operating-rhythm install, Atlas FS-rails enterprise GTM alignment, Vector concept-to-prod cycle, Compass advisory framework).

### Step 6: Generate questions to ask the interviewer

5-7 questions, one tagged as the "closer" (highest-risk-highest-reward final question). Each question must:

- Demonstrate operator-mindset, not interview-question template
- Be specific to the company's actual surface (customer name, vertical, product feature)
- Probe a real product trade-off, not a softball about culture

### Step 7: Generate one-line answers to likely questions back

Cover the standard set:

- "Walk me through your background" (60-second compressed pitch leading with the role-relevant Tier-1 anchor)
- "Why this company / role?"
- "What attracts you about this stage?"
- "What's a question you have about the role we should answer up front?"
- "Do you have AI product experience?" (honest framing on Vector SaaS product depth + Compass operating-model advisory; never conflate the two)
- "Do you have <domain> experience?" (honest framing per the company's vertical)
- "What comp are you thinking?" (defer-volunteering posture; let them surface band first)
- "What's your timeline?"

### Step 8: Generate friction flags + signals + wrap-up signals + do-nots

- **Friction flags to listen for** during the call (signals about the org dynamic, scope reality, what they want)
- **Wrap-up signals to send** by minute 25 (confidence, 90-day posture, curiosity, pointed follow-up, clean next-step ask)
- **Do nots** (don't claim X, don't volunteer Y, etc., specific to this role's friction set)

### Step 9: Save the three artifacts

In `outreach/{slug}/`:

- `prep-{interviewer-slug}-meeting.md` - full markdown packet (long-form, comprehensive)
- `prep-{interviewer-slug}-meeting.html` - interactive HTML with TOC, sidebar, view toggle (Full / Call mode), pre-call checklist with persistent checkboxes, print-friendly CSS
- `prep-{interviewer-slug}-onepager.md` - scannable one-page distillation for live call use

Use the templates at `templates/prep-meeting.md.template`, `templates/prep-meeting.html.template`, `templates/prep-onepager.md.template` as the structural baseline. Always populate the Vector / Compass distinction correctly: Vector is the AI-native SaaS product, Compass is the AI-native operating model advisory.

### Step 10: Update dashboard

Update the role's dashboard entry:

- Append the meeting + interviewer + prep-file paths to `channels` (e.g., `"<interviewer-name> call booked <date> - prep saved"`).
- If status was `pending` or `drafted`, flip to `active`.
- Suspend Day-5 / Day-7 / Day-10 bump watches by adding a note `"bump watches SUSPENDED pending {interviewer_name} call {meeting_when}"`.
- Log the meeting date and interviewer in the note.

### Step 11: Present in chat

Output:

- Headline: who, when, role, primary interviewer LinkedIn URL
- The single most important question to ask (the scope-disambiguation one)
- 2-3 sentence interviewer profile summary
- 1-line strategic framing for the call ("She's a non-CS-degree product leader who upskilled to ML - lean on operating-model language, not theory")
- Computer-link to all three saved files

### Step 12: STOP

Do NOT proceed to send any outreach, schedule the meeting, or generate post-call material. Phase 4 is preparation only. Phase 5 (debrief) handles post-call.

## Approval gates

Before generating the full packet, surface for the user:

- Interviewer name + LinkedIn URL (if auto-found, confirm before writing the packet)
- Conflicting public titles (e.g. LinkedIn says VP Product, TheOrg says Head of Product) - flag and let user pick the canonical read
- Round classification (screen / panel / final / exec) - confirm if ambiguous
- Comp band intel refresh if new public data surfaces

If the interviewer LinkedIn URL search returns ambiguity (multiple profile matches), stop and ask. Do NOT guess.

## Failure modes

- **Interviewer not findable on LinkedIn**: surface the search results, ask user to provide URL. Do not proceed without.
- **Role not in dashboard or jd.md missing**: refuse and route user to phase-2-packet first.
- **Conflicting public titles**: flag both, ask which is current, generate prep with both noted.
- **Founder / CEO with limited public profile**: pull what's available, note the gap, advise user to lean on the company-intel layer rather than personal-research layer.
- **Recruiter screen with no specific interviewer named (generic "Talent Team")**: generate a recruiter-screen variant of the packet without per-person research, focused on comp-pre-disclosure, work-auth, timeline, role-rank-in-pipeline.

## Output discipline

- No em or en dashes anywhere in the packet (per `outreach-style.yaml`).
- Vector / Compass distinction respected explicitly (per `feedback_cimanote_vs_kairos.md` memory).
- Profile-view inbound signals treated as neutral per `feedback_profile_view_signal.md` memory.
- Geo header conditional per `geo-rules.cv_header_templates`.

## References

- `/skills/phase-4-prep/references/meeting-prep-recipes.md` - canonical recipes per round + interviewer altitude.
- `/skills/phase-4-prep/references/interviewer-research-patterns.md` - LinkedIn + TheOrg + Crunchbase + web search patterns, public-record conflict resolution.
- Canonical example: see `outreach/{slug}/prep-sam-meeting.md` + `.html` + `prep-sam-onepager.md` in the user's project.
