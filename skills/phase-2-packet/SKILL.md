---
name: phase-2-packet
description: Build a Phase 2 outreach packet for a single greenlit role. Triggers on "build packet for X", "tailor CV for X", "Phase 2", "packet X", "/packet", or any request to prepare an application for a specific company / role. Pulls the full JD via the ATS redirect, identifies the right contacts, generates a JD-tailored CV (docx + PDF) per the discipline rules, drafts channel-appropriate outreach (Connect+Note + longer DM), and saves the packet under outreach/{slug}/. Stops before Phase 3 - waits for the user's explicit "send" approval.
---

# phase-2-packet

Build the Phase 2 outreach packet for a single role. Pull the JD, identify contacts, tailor the CV, draft outreach, save the packet, present in chat.

## When to invoke

The user says: "build packet for X", "tailor CV for X", "Phase 2 for X", "packet X", "/packet X", or "let's go" after a Phase 1 greenlight summary.

## Inputs

The user names a role by company or by slug. Resolve to:

- `company` (string)
- `role_title` (string)
- `linkedin_url` (the `/jobs/view/{id}/` URL)
- `slug` (kebab-case, e.g. `company-role-slug`)

If the role is in the dashboard but no slug yet, generate one. If the role isn't in the dashboard, scaffold a minimal entry first.

## Workflow

### Step 1: Pull the full JD

Delegate to the `jd-extractor` agent (or run inline). The LinkedIn jobs page renders a skeleton in unauthenticated views; the real body lives behind the "Apply on company website" redirect. Recover it via:

1. Navigate to the LinkedIn jobs URL in Chrome
2. Find the Apply link's `href`
3. Decode the `/safety/go/?url=...` query param to recover the destination ATS URL
4. Navigate to the destination (Teamtailor, Workable, Greenhouse, Lever, Ashby, company-careers page)
5. Extract the full JD body text including:
   - About the role / mission
   - Responsibilities / day-in-the-life
   - Required experience / qualifications
   - Comp band if stated
   - Anti-bot screener words / phrases (look for `mention the word "..."` or `include "..." in your application`)
   - Reporting line and sit-on-SLT signals
   - Customer / partner names called out by name
   - In-office requirement (number of days)
   - Pre-employment check requirements (FCA, security clearance, criminal/credit checks)

### Step 2: Sanity-check tier classification

If the JD body reveals signals that contradict the Phase-1 card-level triage (e.g., title says "Head of Product" but body says "individual contributor / chief of staff"), STOP. Surface the mismatch to the user with two options:

- A) **Skip** - reclassify as Skip, log reason
- B) **Reframe and proceed** - tailor for the actual scope (e.g., "I have been the CPO three times; force-multiplier IC at this scale-up is by choice")
- C) **Apply low-effort** - careers application only, no Connect+Note, no CV refresh

Do NOT proceed to Step 3 without the user's call.

### Step 3: Identify contacts

Apply the contact-discovery cascade from `${CLAUDE_PLUGIN_ROOT}/config/channels.yaml`:

1. LinkedIn job poster (the "Meet the hiring team" panel)
2. Hiring manager named in JD body (often "Reports to: ..." or specific name)
3. 1st-degree connection at the company in product/eng leadership
4. 2nd-degree with strong mutuals
5. Founder / CEO for founder-led companies
6. Recruiter-first (de-anon path) for recruiter-masked listings

For each candidate contact, check:

- Degree of connection (1st / 2nd / 3rd)
- Open Profile status (do they show a `Message` button without InMail paywall?)
- Public LinkedIn URL

When the role's reporting-to-CTO is in another timezone or appears to be transitioning out (e.g., now CEO at a different company), consider parallel reach to both the CTO and the CEO of the hiring company.

### Step 4: Tailor the CV

Delegate to the `cv-tailor` agent. Pass:

- `--role-slug` - the kebab slug
- `--baseline` - path to the user's master CV (default: `${CLAUDE_PLUGIN_ROOT}/templates/cv-baseline.docx`, but the user may have replaced this with their own)
- Replacements derived from the JD per the discipline:
  - Headline-positioning fragment (one phrase that captures the role's mandate)
  - Adjacency sentence (last sentence of executive summary, lands the role-specific analogue)
  - One or two career-highlight cells (rename + body)
  - Italic context line per relevant past role
  - Geo-conditional header per `geo-rules.cv_header_templates`
  - "Tailored for {company}, {role}" tag

The agent applies the discipline rules from `outreach-style.yaml`:

- Identity stable
- Max 2 of 6 highlight cells changed
- One phrase per past role's italic context line
- No em/en dashes anywhere
- Geo header conditional

Outputs `{cv_filename_prefix}-{slug}.docx` and `.pdf` in `outreach/{slug}/`.

### Step 5: Draft outreach

Delegate to the `outreach-drafter` agent. Generate:

1. **Connect+Note (Premium 300 char or standard 280 char)** for the primary contact, leading with one concrete JD hook + one pattern-match anchor
2. **Connect+Note** for the backup contact (parallel reach)
3. **Longer DM (120-180 words)** for use after a connection accepts, or if Open Profile path lands

Apply `outreach-style.yaml` rules: peer-to-peer, no banned phrases, no em/en dashes, signed off with first name.

For role-specific anti-bot screener words detected in the JD body, draft a Summary / cover-letter blurb that includes the word naturally (per `outreach-style.yaml.screener_test_words.action`).

### Step 6: Save the packet

Create `outreach/{slug}/` and write:

- `{cv_filename_prefix}-{slug}.docx`
- `{cv_filename_prefix}-{slug}.pdf`
- `jd.md` - JD notes from `${CLAUDE_PLUGIN_ROOT}/templates/jd.md.template`, populated
- `outreach.md` - outreach drafts from `${CLAUDE_PLUGIN_ROOT}/templates/outreach.md.template`, populated

### Step 7: Append to dashboard

Append a new role entry to the dashboard's `ROLES = [...]` array with:

- `id` - one greater than the current max
- `slug` - the kebab slug
- `role`, `company`, `location`, `comp`, `score`
- `jdUrl` - the canonical `/jobs/view/{id}/` URL (NOT the search URL)
- `contact` - primary contact name + role
- `contactUrl` - primary contact's LinkedIn URL
- `channels` - planned channels
- `sendDate: null` - until Phase 3
- `status: "drafted"`
- `note` - long-form note capturing the score rationale, friction flags, and pattern match anchors

### Step 8: Present in chat

Output:

- Score and tier
- JD URL + primary contact LinkedIn URL (per `feedback_packet_links.md` rule: ALWAYS show JD URL + contact URL in chat at greenlight, not just in saved files)
- Connect+Note draft (verbatim, with char count)
- Friction flags worth confirming with the user before send
- Computer:// links to the saved CV PDF, DOCX, jd.md, outreach.md

### Step 9: STOP

Do NOT proceed to Phase 3. Wait for the user's explicit "send" per role.

## Approval gate

Before saving the packet, surface for the user:

- Tier classification post-JD-extraction (may have changed from Phase 1)
- Comp band alignment
- Geo friction
- Title-scope alignment (line-product vs IC vs specialist)

If any of these have shifted from the Phase-1 read, surface the shift before generating the CV. The user gets the call.

## References

See `${CLAUDE_PLUGIN_ROOT}/skills/phase-2-packet/references/cv-tailoring-discipline.md` for the canonical replacement-key pattern. See `${CLAUDE_PLUGIN_ROOT}/skills/phase-2-packet/references/contact-discovery-recipes.md` for LinkedIn search patterns to identify contacts.
