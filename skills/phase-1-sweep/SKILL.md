---
name: phase-1-sweep
description: Run the daily Phase 1 sweep for senior product leadership roles. Triggers on "run today's sweep", "Phase 1", "find new roles", "/sweep", "what's new today", "morning sweep", "scan LinkedIn for product roles". Sources roles from LinkedIn AND directly from major ATS domains (Greenhouse, Lever, Workday, Ashby, etc.) via Google site: search, pulls JD bodies via the apply-link redirect or direct fetch, scores each role 1-10 against the user's ICP and scoring weights, dedupes against the existing dashboard, and produces a Tier-1 / Tier-2 / Skip greenlight summary. Stops before Phase 2 - waits for the user's per-role greenlight.
---

# phase-1-sweep

Run the daily Phase 1 sweep. Source new roles from LinkedIn AND directly from major ATS domains, score, dedupe, triage, and produce the greenlight summary.

## When to invoke

The user says: "run today's sweep", "Phase 1", "find new roles", "what's new today", "morning sweep", "scan LinkedIn for product roles", "/sweep". Or this skill is fired by a scheduled task at 9am [Operator Home City] time.

## Required setup

Before running:

1. Read `${CLAUDE_PLUGIN_ROOT}/config/icp.yaml` for target titles, stage filters, sector filters, recruiter-masked handling
2. Read `${CLAUDE_PLUGIN_ROOT}/config/geo-rules.yaml` for sourcing regions
3. Read `${CLAUDE_PLUGIN_ROOT}/config/scoring.yaml` for dimensional weights and tier thresholds
4. Read `${CLAUDE_PLUGIN_ROOT}/config/ats-sources.yaml` for ATS domains, liveness signals, query caps (used by Step 1B)
5. Identify the user's project folder. If a `dashboard.html` exists there, parse the `ROLES = [...]` array for dedupe. If not, scaffold one from `${CLAUDE_PLUGIN_ROOT}/templates/dashboard.html`.

## Workflow

### Step 1A: LinkedIn sweep

For each region in `geo-rules.sourcing_regions` and each title pattern in `icp.target_titles`:

1. Open Chrome via the Claude in Chrome MCP (call `mcp__Claude_in_Chrome__list_connected_browsers` -> `select_browser`).
2. Navigate to a LinkedIn job-search URL with the title-OR-pattern, the region, `f_TPR=r86400` (last 24h), `sortBy=DD`. For US Remote add `f_WT=2,3` for Remote+Hybrid filter.
3. Extract job listings via JavaScript: collect `(jobId, title, company, location, posted, applicants_count)` for each card visible in the results pane.
4. Scroll the virtualized list to load all results; collect total count.

Cover the LinkedIn keyword pluralization gap explicitly - both "VP of Product" and "VP Products" search variants.

### Step 1B: ATS-Google sweep (NEW in v0.2.0)

In parallel with the LinkedIn sweep, delegate to the `ats-google-sweep` agent. This catches roles that never reach LinkedIn or arrive there days late.

Inputs to the agent:
- `regions`: same set as Step 1A
- `title_cluster`: from `icp.target_titles`
- `ats_domains`: from `config/ats-sources.yaml ats_domains[]`
- `existing_dashboard_urls`: parsed from `dashboard.ROLES[]`

The agent handles:
- Building per-region site: queries against each ATS domain (Greenhouse, Lever, Workday, Ashby, iCIMS, Jobvite, BambooHR, SmartRecruiters, Workable, Teamtailor)
- Liveness check on each URL BEFORE body fetch (critical: Google's index lags ATS reality)
- Routing SPA-based ATSs (Ashby, Workday) through `jd-extractor` for Chrome render
- Recruiter-mask check against `icp.recruiter_masked_known_aggregators`

Returns a list of candidates in the same shape as Step 1A but with `source: "ats-google"` and `score_confidence: medium` by default (see `ats-sources.yaml`).

### Step 2: Dedupe (across both sources)

Merge the LinkedIn (Step 1A) and ATS (Step 1B) candidate lists. For each candidate role, match against `dashboard.ROLES[]` by:

1. URL exact match
2. `(company, role_title)` substring match

Skip duplicates. Cross-source dedupe: if the same role appears on both LinkedIn and the ATS (common case for high-profile roles), prefer the LinkedIn entry (richer metadata: applicants_count, posted timestamp, recruiter_masked detection at LinkedIn level) but record the ATS URL in a `secondary_url` field for completeness.

Note: companies with multiple listings (e.g., The AA London Hybrid + The AA Basingstoke Hybrid for the same role) should be deduplicated to a single entry, with the better location captured.

### Step 3: Pull full JD via ATS redirect (LinkedIn-sourced roles only)

For each truly new LinkedIn-sourced role, do NOT score from the LinkedIn card alone. The card is a skeleton; titles regularly misclassify the actual JD body. Delegate to the `jd-extractor` agent (or run inline):

1. Find the "Apply on company website" link on the LinkedIn job page.
2. Extract the destination URL from the `/safety/go/?url=...` redirect param.
3. Navigate to the destination ATS (Teamtailor, Workable, Greenhouse, Lever, Ashby, custom careers page).
4. Extract the full JD body text.
5. Cache the body keyed by jobId to avoid duplicate fetches.

ATS-Google-sourced roles (Step 1B) already have the JD body fetched by the agent, so this step is skipped for them. They flow directly to Step 4.

### Step 4: Score

For each role with a full JD body:

1. Apply the dimensional scoring per `scoring.yaml` weights: stage, domain, scope, comp, geo, founder_quality, ai_native_signal, founder_partnership.
2. Apply hard blockers from `scoring.hard_blockers`. Hard blocker -> drop the role entirely.
3. Apply post-JD-extraction checks for IC framing, FCA-specialist signals, sub-VP scope. These can downgrade by one tier.
4. Apply title red flags from `icp.title_red_flags` and JD-body red flags from `icp.jd_body_red_flags`.
5. Apply `score_confidence` discount: ATS-Google-sourced roles default to `medium` (per `ats-sources.yaml`); LinkedIn card-only with no body extraction is `low`; LinkedIn + extracted body is `medium`; LinkedIn + body + verified contacts + comp band is `high`. Confidence does not change the numeric score; it controls how aggressively to greenlight.
6. Final score 1-10.

### Step 5: Triage

- **Tier 1** = score >= `scoring.tier_1_threshold` AND no hard blockers AND no major friction
- **Tier 2** = score >= `scoring.tier_2_threshold` with manageable friction (geo-flexibility cost, hybrid commute, narrower-than-CPO scope, recruiter-masked, ATS-only body-extraction-failed)
- **Skip** = below `scoring.skip_below` OR hard blocker OR clear structural mismatch revealed by JD body

For recruiter-masked listings from known aggregators (`icp.recruiter_masked_known_aggregators`), default to Skip unless the user has explicitly overridden. Surface as a flagged Skip with the de-anon-then-pursue alternative noted.

For ATS-Google-sourced roles where body extraction failed (snippet-only data), default to Tier 2 with a `body_unreachable` flag so the user can manually open the URL.

### Step 6: Produce greenlight summary

Output a chat-ready summary with:

- New roles count by tier, broken down by source: LinkedIn vs ATS-Google
- One-line summary per Tier-1 role: score, fit signals, friction flags, JD URL, source label
- Quick-glance Tier-2 list with the friction flag callout per role
- Skipped roles with one-line reason
- Recommendation on which to greenlight for Phase 2/3

Also produce the **Today's Actions follow-up tracker** by reading the dashboard:

- Roles in Day-5 to Day-7 bump window (sendDate today minus 5-7 days)
- Roles past Day-10 final-action threshold

### Step 7: STOP

Do NOT proceed to Phase 2. Wait for the user's explicit greenlight. Do NOT generate CVs, do NOT draft outreach, do NOT identify contacts deeply. The Phase 1 deliverable is decision-ready triage, not action.

## Output discipline

The summary in chat should:

- Lead with new roles count by tier and source (LinkedIn vs ATS-Google)
- Tier-1 entries get a 3-4 line per-role block with score, fit signals, friction, JD URL, source
- Tier-2 entries get a one-line each
- Skipped entries get a one-line reason each
- End with a recommendation and the follow-up tracker

Do NOT use em or en dashes anywhere (per `outreach-style.yaml`). Do NOT include trailing summaries.

## Schedule integration

The plugin can be triggered on a 9am [Operator Home City]-time daily schedule via Cowork's scheduled task system:

```
mcp__scheduled-tasks__create_scheduled_task with prompt: "Run the phase-1-sweep skill"
```

The user installs this scheduled task once at plugin setup time (see README.md).

## Failure modes to watch

- **LinkedIn auth lapsed**: Chrome shows logged-out state -> tell the user to log in, retry
- **JD body unreachable**: ATS rate-limit or login wall -> note "JD body not extracted" in the role, score from card-only data, mark `score_confidence: low`
- **Promoted listings bleed through date filter**: ignore "Promoted" listings unless explicitly within 24h window per the timestamp
- **Blocked URL extraction**: when the apply-link redirect URL is blocked from JS extraction, fall back to clicking Apply and reading the resulting tab URL via tabs_context_mcp
- **ATS-Google staleness (NEW)**: ~75% of Google-indexed ATS URLs are stale. The `ats-google-sweep` agent runs liveness checks pre-fetch; staleness should rarely surface to the user.
- **Google rate-limit on site: queries**: agent continues with remaining queries; lost queries logged in the run report.

## References

- `${CLAUDE_PLUGIN_ROOT}/skills/phase-1-sweep/references/linkedin-search-recipes.md` - canonical LinkedIn search-URL builder patterns by region.
- `${CLAUDE_PLUGIN_ROOT}/skills/phase-1-sweep/references/jd-extraction-patterns.md` - ATS-specific extraction patterns.
- `${CLAUDE_PLUGIN_ROOT}/skills/phase-1-sweep/references/ats-google-recipes.md` - canonical Google site: query patterns and per-ATS liveness signals (NEW in v0.2.0).
