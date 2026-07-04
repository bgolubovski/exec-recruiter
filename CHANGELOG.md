# Changelog

All notable changes to the exec-recruiter plugin.

## v0.5.2 (2026-07-05)

### Fixed

- **CV tailored-for flow rebuilt around insertion.** The baseline CV no longer carries a "Tailored for {company}, {role}" line (the old one was removed per operator direction), which broke the string-replacement anchor the tailoring flow relied on. `scripts/tailor_cv.py` now takes a `--tailored-for` flag and inserts the tag as a small italic gray centered paragraph between the contact line and the EXECUTIVE SUMMARY heading. `agents/cv-tailor.md` Step 2 and Step 3 updated accordingly: the tag is passed via the flag, never derived as a replacement pair.
- **PDF conversion binary fallback.** `tailor_cv.py` now resolves `libreoffice` OR `soffice` from PATH instead of hardcoding `libreoffice` (macOS Homebrew installs only ship `soffice`).

### Changed

- **Verification text-index map re-derived** against the new baseline and confirmed empirically: `[1,2,8,10,12,13,36,53]` = headline, geo, tailored-for tag (inserted), adjacency, first highlight cell title, first highlight cell body, Northstar italic, Helix italic. The map is documented as valid only for the tailored output (post-insertion); the bare baseline sits one index lower from EXECUTIVE SUMMARY onward.
- **Highlight-cell swap examples updated**: the cell formerly titled "Sales-Led Culture Navigation" is now "Inflection-Point Operator"; `cv-tailor.md` examples reference the new title, plus a caution that replacement old-strings must be unique in document.xml (the old title still exists in CORE COMPETENCIES and would be corrupted by a global replace).
- **`templates/CV-REQUIREMENTS.md`** now documents that the tailored-for line must NOT be present in the baseline and that the index map must be derived from a tailored output.
- **Baseline refresh**: `templates/cv-baseline.docx` neutralized (tailored-for paragraph removed); `cv-baseline-reference.pdf` regenerated to match.

## v0.5.1 (2026-05-20)

### Fixed

- **Dashboard engagement-signal classifier**: `getEngagementSignal()` previously short-circuited on `r.status === 'replied'` before checking the interview regex, which meant any replied-status role with an interview phrase in its note (e.g., "interview invite", "interview scheduled", "advanced to next round") could not appear in the Interview funnel card. Reordered so the interview regex check runs first. The funnel widget's cumulative roll-up (`replied = replied + interview`) already handles double-counting correctly, so interview-stage roles now correctly appear in BOTH the Replied counter (via status field) AND the Interview funnel card (via note regex).

### Added

- **`nextActions` (and `nextAction` shorthand) on the role schema**. The `pendingMilestones()` function now emits two classes of calendar milestones:
  - **(a) Outreach-cycle milestones** (Day-5 / Day-7 / Day-10 bumps), automatically generated for `status: "pending"` roles with a `sendDate`. Unchanged behavior.
  - **(b) Custom next-action milestones**, read from a `nextActions` array on the role object. Applies to any status that isn't rejected or skipped.

  Schema:
  ```js
  nextActions: [
    { date: "2026-05-20", action: "Reply to interviewer with time slots", urgency: "hard" },
    { date: "2026-05-22", action: "If no interview scheduled, follow up", urgency: "mid" }
  ]
  ```

  Single-action shorthand also supported: `nextAction: "..."` + `nextActionDate: "..."` + optional `nextActionUrgency`.

  Use `nextActions` whenever an interview-stage role has a known time-bound action (reply with slots, prep day-before, post-call summary, etc.). Without it, the calendar would be silent on advanced roles since outreach-cycle milestones only fire for pending status.

### Notes

- These fixes were prompted by an interview-stage role that disappeared from both the Interview funnel card and the bottom calendar table after its status was advanced to `replied`. Both fixes are backward-compatible: existing pending-status roles continue to receive the standard Day-5/7/10 milestone cycle, and roles without a `nextActions` field behave exactly as before.
- The combined rule when a role advances to interview stage: (1) set `status: "replied"`, (2) add at least one interview-regex-matching phrase to the note, (3) add a `nextActions` array with date-bound next-steps.

## v0.5.0 (2026-05-14)

### Added

- **Phase 4: meeting prep** (`skills/phase-4-prep/`). Build an interview / screening-call prep packet for a booked conversation on a specific role. Pulls role context from the dashboard, researches the interviewer (LinkedIn + TheOrg + Crunchbase + web), refreshes company intel, generates the scope-disambiguation question (varies by round + altitude), first-90-days narrative (single or three branched), questions to ask, one-line answers to likely questions back, comp posture, friction flags, and a wrap-up signal checklist. Saves three artifacts: full markdown, interactive HTML, scannable one-pager.
  - Supports rounds: `screen`, `working-session`, `panel`, `final`, `exec`, `reference-check-prep`.
  - `--deep` flag triggers maximum-depth company intel research.
  - Templates: `templates/prep-meeting.md.template`, `templates/prep-meeting.html.template`, `templates/prep-onepager.md.template`.
  - References: `meeting-prep-recipes.md` (per-round and per-altitude recipes), `interviewer-research-patterns.md` (research sources, conflict resolution, what NOT to research).
  - Canonical example structure shipped: see `templates/prep-meeting.html.template` for the full interactive packet skeleton.
- **Phase 5: call debrief** (`skills/phase-5-debrief/`). Process post-call notes after a Phase-4-prepped meeting. Parses what was said, captures scope / comp / process / friction signals, structures a debrief artifact, updates the dashboard, suggests next-action (prep-next-round, send-thank-you-and-wait, send-requested-materials, passive-watch, mark-rejected, escalate-to-different-contact), and prompts for memory writes when patterns emerge.
- **meeting-prep-researcher agent** (`agents/meeting-prep-researcher.md`). Dedicated agent for interviewer research + company intel refresh, used by Phase 4. Pulls LinkedIn + TheOrg + Crunchbase + web search + Wikipedia where applicable. Cross-references for title conflicts. Returns a structured intel object to phase-4-prep.
- **New keywords**: `interview-prep`, `meeting-prep`, `call-debrief`.

### Changed

- Plugin description updated to reflect the new five-phase pipeline (sourcing → packet → send → prep → debrief).
- Phases 4 and 5 are user-invoked only. They never auto-fire from dashboard signals.
- The Vector / Compass distinction is enforced explicitly in Phase 4 templates and references. Vector is the AI-native SaaS product; Compass is the AI-native operating model advisory. They sit at different layers and must not be conflated.
- Profile-view inbound signals are treated as neutral per `feedback_profile_view_signal.md`. Phase 5 does not classify them as positive engagement.

### Notes

- Phase 4 and Phase 5 are designed as a pair. Phase 5 grades the call against Phase 4's predictions; calibration improves the templates over time.
- The HTML prep packet template (`prep-meeting.html.template`) includes: dark-mode-friendly light-mode UI, sticky left TOC, sticky right sidebar with always-visible quick-reference, view toggle (Full / Call mode), persistent checkboxes via sessionStorage, print-friendly CSS, no external dependencies.
- Phase 4 does NOT draft outreach. Thank-you DMs, post-meeting Connect+Notes, and follow-up emails remain in the existing `outreach-drafter` agent invoked from Phase 2 or manually.

## v0.4.0 (2026-05-12)

### Added

- **Rich live dashboard template** (`templates/dashboard.html`): full-featured replacement for the minimal scaffold.
  - Dark-mode UI with calibrated color tokens
  - Stats panels: total pending, total replied, follow-up window counts, rejection rates
  - Today's Actions tracker: roles due Day-5 bump, Day-7 second-touch, Day-10 final, plus profile-view / mutual-connection inbound signals
  - Cohort views: pending by sendDate cohort with status breakdown
  - Score histogram across the active pipeline
  - Domain breakdown chart (B2B SaaS, FS, healthcare, etc.) by status
  - Notes drawer for long-form per-role context
  - Card-style filter chips (status, channel, search)
  - Compact-mode toggle for high-density scanning
  - Computer-link integration to CV PDF / DOCX / jd.md / outreach.md per role
- **CHANGELOG.md** to track future plugin version history

### Changed

- Plugin description updated to surface the new dashboard capabilities
- `dashboard` keyword added

### Notes

- The dashboard template ships with an empty `ROLES = [];` array; phase-1-sweep / phase-2-packet / phase-3-send workflows populate it over time.
- The CV file-link pattern (`Operator-FirstName-CV-{slug}.pdf`) is consistent with the cv-tailor agent and the phase-2-packet skill output convention. To re-brand for a different operator, update the prefix in `templates/dashboard.html` (line ~905) and in `scripts/tailor_cv.py`.

## v0.2.0 (2026-05-09)

### Added

- **Step 1B in phase-1-sweep**: parallel ATS-Google sweep alongside the LinkedIn sweep
- **ats-google-sweep agent** (`agents/ats-google-sweep.md`): searches 10 major ATS domains (Greenhouse, Lever, Workday, Ashby, iCIMS, Jobvite, BambooHR, SmartRecruiters, Workable, Teamtailor) via Google `site:` operator
- **ATS sources config** (`config/ats-sources.yaml`): per-ATS domain, body-extraction method (web_fetch vs chrome render), liveness signals, query construction rules, result caps
- **Liveness check before body fetch**: classifies stale / pulled / SPA-shell URLs to avoid wasted fetches (Google indexes ATS pages fast but de-indexes slowly)
- **Chrome-render routing for SPA-based ATSs** (Ashby, Workday) through the existing jd-extractor agent
- **ats-google-recipes.md reference** (`skills/phase-1-sweep/references/ats-google-recipes.md`): canonical site: query patterns and per-ATS liveness signals

### Changed

- phase-1-sweep workflow restructured: Step 1A (LinkedIn) and Step 1B (ATS-Google) run in parallel, results merged at Step 2 dedupe
- Score confidence model updated: ATS-Google-sourced roles default to `medium` confidence, LinkedIn card-only is `low`, LinkedIn + body is `medium`, LinkedIn + body + verified contacts + comp is `high`

### Failure modes addressed

- Recruiter-aggregator pollution at ATS level (filtered via icp.recruiter_masked_known_aggregators)
- Google rate-limit on `site:` queries (continue with remaining queries, log lost ones)
- SPA-shell URLs that need JS rendering (routed to jd-extractor)

## v0.1.0 (2026-05-08)

### Initial release

- **Skills**: phase-1-sweep, phase-2-packet, phase-3-send, score-role, daily-bump, dashboard-status
- **Agents**: jd-extractor, cv-tailor, outreach-drafter
- **Configs**: icp.yaml, geo-rules.yaml, scoring.yaml, channels.yaml, outreach-style.yaml, follow-up.yaml
- **Templates**: dashboard.html scaffold, jd.md.template, outreach.md.template, cv-baseline.docx, cv-baseline-reference.pdf
- **Scripts**: tailor_cv.py for XML-level docx text replacement (no python-docx dependency)
