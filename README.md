# exec-recruiter

A personal executive recruiter for Product Leadership job hunts (CPO, VP/SVP Product, Head of Product at scale). The plugin runs the full pipeline: daily sourcing, fit-scored triage, JD-tailored CV generation, contact-aware outreach drafts, approval-gated sends, meeting / interview prep with interviewer research, and post-call debrief. Built for senior product operators who want a recruiter-grade workflow without burning a recruiter retainer.

## What it does

Five phases, all approval-gated.

**Phase 1: Source and rank.** Sweeps LinkedIn AND major ATS domains (Greenhouse, Lever, Workday, Ashby, iCIMS, Jobvite, BambooHR, SmartRecruiters, Workable, Teamtailor) via Google `site:` operator. Pulls full JDs via the apply-link redirect to the underlying ATS or directly from the ATS, scores each role 1-10 against your fit criteria, dedupes against your existing dashboard, and produces a Tier 1 / Tier 2 / Skip greenlight summary.

**Phase 2: Packet build.** For each role you greenlight, identifies the right contact (job poster, hiring manager, 1st-degree, 2nd-degree mutuals), tailors the CV to the JD using a discipline that keeps identity stable (only the adjacency sentence, one or two highlight cells, and per-role italic context lines change), and drafts channel-appropriate outreach (Connect+Note, longer DM if Open Profile available, InMail as last resort).

**Phase 3: Send.** Walks you through send one role at a time. The plugin opens the right LinkedIn surface, types the message into the field, and stops. You click Send. No autonomous sending.

**Phase 4: Meeting / interview prep.** When a contact accepts, replies, or books a meeting, the plugin builds a prep packet for the call. Researches the named interviewer (LinkedIn, TheOrg, Crunchbase, web), refreshes company intel, generates the scope-disambiguation question, first-90-days narrative (with branches if scope is ambiguous), questions to ask, one-line answers to likely questions back, comp posture, friction flags, and a wrap-up signal checklist. Saves three artifacts per call: full markdown, interactive HTML with TOC and Call-mode toggle, and a scannable one-page card. Supports rounds: `screen`, `working-session`, `panel`, `final`, `exec`, `reference-check-prep`. `--deep` flag triggers maximum-depth company intel.

**Phase 5: Post-call debrief.** After a Phase-4-prepped call, the user pastes their notes. The plugin parses what was said, captures scope / comp / process / friction signals, structures a debrief artifact, updates the dashboard, and identifies the next action (prep next round, send thank-you and wait, send requested materials, passive watch, mark rejected, or escalate to a different contact). Prompts for memory writes when patterns emerge that contradict prior assumptions.

## Configurable surface

Seven config files in `config/` define the user-tunable parts. Edit them at install time, then re-run.

- `icp.yaml` - target role titles, search keywords, seniority, sector preferences
- `geo-rules.yaml` - default location, opt-in regions, geo-conditional CV header strings
- `scoring.yaml` - dimension weights for the 1-10 fit score (stage, domain, scope, comp, geo, founder, etc.)
- `channels.yaml` - DM / Connect+Note / InMail order, credit-preservation rules, character limits
- `follow-up.yaml` - Day-5 / Day-7 / Day-10 thresholds for bumps and final-action
- `outreach-style.yaml` - tone, banned punctuation (em/en dashes), sign-off, language
- `ats-sources.yaml` - the 10 ATS domains scanned in Phase 1B, with per-ATS liveness checks and SPA-render routing

## CV baseline

The plugin does NOT ship with a CV baseline. Place your own master CV at `templates/cv-baseline.docx` (any executive product CV will do). The tailoring discipline preserves your identity blocks (name, headline scaffold, work history dates, education) and only swaps:

1. The headline-positioning fragment
2. The adjacency sentence at the end of the executive summary
3. One or two career-highlight cells (out of six)
4. The italic context line per past role
5. The geo-conditional header

This lets you ship a JD-tailored CV without the false-positive rebuild risk. The structural expectations are documented in `scripts/tailor_cv.py` and `agents/cv-tailor.md`.

Note: the CV filename convention currently includes the operator's name (e.g. `Operator-FirstName-CV-<slug>.docx`). To use this plugin as-is, customize the prefix in `scripts/tailor_cv.py` and `agents/cv-tailor.md` to match your own name, OR wait for the planned `config/operator.yaml` parameterization in a future version.

## Skills

| Skill | Triggers on |
|---|---|
| `phase-1-sweep` | "run today's sweep", "Phase 1", "find new roles" |
| `phase-2-packet` | "build packet for X", "tailor CV for X", "Phase 2" |
| `phase-3-send` | "send X", "Phase 3", "ready to send" |
| `phase-4-prep` | "prep for X", "build prep packet for X", "interview prep X", "/prep <slug>" |
| `phase-5-debrief` | "debrief X", "log my call with X", "/debrief <slug>" |
| `score-role` | "score this JD", "is this role a fit" |
| `daily-bump` | "what bumps today", "Day-5 follow-ups" |
| `dashboard-status` | "where do I stand", "today's actions" |

## Agents

- `jd-extractor` - pulls full JDs via the LinkedIn-to-ATS redirect URL extraction trick (Teamtailor, Workable, Greenhouse, Lever, Ashby, company-careers pages). Solves the LinkedIn-skeleton-view problem.
- `ats-google-sweep` - searches the 10 major ATS domains via Google `site:` operator. Liveness-checks every URL before fetching, routes SPA-based ATSs (Ashby, Workday) through Chrome render.
- `cv-tailor` - applies the tailoring discipline rules to the CV docx, regenerates PDF via libreoffice.
- `outreach-drafter` - generates Connect+Notes (300 char Premium / 280 standard), longer DMs, and InMail variants per channel preferences.
- `meeting-prep-researcher` - researches a named interviewer (LinkedIn, TheOrg, Crunchbase, web) and refreshes company intel for Phase 4 prep packets.

## Templates

- `templates/dashboard.html` - rich live dashboard with cohort views, score histogram, domain breakdown chart, follow-up tracker, inbound-signal detection. Ships with empty `ROLES = []`; phase-1/2/3/4/5 workflows populate it over time.
- `templates/jd.md.template` - JD-capture template used by Phase 2
- `templates/outreach.md.template` - outreach drafts template used by Phase 2
- `templates/prep-meeting.md.template` - full markdown prep packet template used by Phase 4
- `templates/prep-meeting.html.template` - interactive HTML prep packet (light-mode UI, sticky TOC, sticky sidebar, view toggle Full / Call mode, persistent checkboxes, print-friendly CSS) used by Phase 4
- `templates/prep-onepager.md.template` - scannable one-page prep card used by Phase 4

## Required connectors

| Category | Required for | Options |
|---|---|---|
| Browser | LinkedIn navigation, JD extraction, send-flow positioning | Claude in Chrome MCP |
| Shell | File ops, libreoffice for PDF generation | Workspace bash (built-in) |
| Web search | ATS-direct sourcing, interviewer research, company intel refresh | WebSearch tool (built-in) |
| Web fetch | LinkedIn / ATS / TheOrg / Crunchbase fetches | mcp__workspace__web_fetch (built-in) |
| Contact enrichment (optional) | Better contact identification when 1st/2nd-degree path is unclear | Apollo MCP |
| Calendar (optional) | Scheduled task setup for daily 9am sweep | Cowork scheduled tasks (built-in) |

## Setup

1. Install the plugin
2. Edit the seven YAML files in `config/` to match your ICP, geo rules, scoring weights, channel preferences, follow-up windows, outreach style, and ATS sources
3. Drop your own master CV in `templates/cv-baseline.docx` (keep the section structure: name + headline + tailored fragment, executive summary with adjacency sentence at end, six-cell career-highlight grid, experience with italic context line per role, core competencies, thought leadership, education)
4. Customize the CV filename prefix in `scripts/tailor_cv.py` + `agents/cv-tailor.md` from `Operator-FirstName-CV-` to match your own name, OR rename consistently
5. Initialize a working dashboard: copy `templates/dashboard.html` to your project folder
6. Customize the operator-personal placeholders in `templates/prep-meeting.html.template` (anchor names, comp range, location, etc.) OR let Phase 4 populate them at runtime from your actual project context
7. Trigger your first sweep with `Phase 1` or "run today's sweep"
8. Optional: set up the daily 9am scheduled sweep via `mcp__scheduled-tasks__create_scheduled_task` (the `phase-1-sweep` skill includes the command)

## Memory and state

The plugin keeps no persistent state of its own. Per-role packets live under `outreach/{slug}/` in your project folder. Status, follow-up windows, and inbound signals are tracked in `dashboard.html`. Loss of plugin state never loses your sourcing history.

## Send safety

No skill in this plugin sends a LinkedIn message, an email, or an application autonomously. Every send is a two-step: the plugin types into the right field and stops; you click Send. The Phase 3 skill explicitly enumerates the approval gate before each action. Phase 4 generates prep material only; it never sends outreach. Phase 5 captures debrief notes only; it updates the dashboard but never sends follow-up messages.

## Versioning

See `CHANGELOG.md` for the full version history. Current version: 0.5.0.
