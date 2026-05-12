# Changelog

All notable changes to the exec-recruiter plugin.

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
- The CV file-link pattern (`Golubovski-Blagoja-CV-{slug}.pdf`) is consistent with the cv-tailor agent and the phase-2-packet skill output convention. To re-brand for a different operator, update the prefix in `templates/dashboard.html` (line ~905) and in `scripts/tailor_cv.py`.

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
