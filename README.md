# exec-recruiter

A personal executive recruiter for senior Product Leadership job hunts (CPO, VP/SVP Product, Head of Product at scale). The plugin runs the full pipeline: daily sourcing, fit-scored triage, JD-tailored CV generation, contact-aware outreach drafts, and approval-gated sends. Built for senior product operators who want a recruiter-grade workflow without burning a recruiter retainer.

## What it does

Three phases, all approval-gated.

**Phase 1: Source and rank.** Sweeps LinkedIn AND directly searches the major ATS domains (Greenhouse, Lever, Workday, Ashby, iCIMS, Jobvite, BambooHR, SmartRecruiters, Workable, Teamtailor) via Google's `site:` operator on a daily schedule. Pulls full JDs via the LinkedIn-to-ATS apply-link redirect or directly from the ATS, scores each role 1-10 against your fit criteria, dedupes across both sources and against your existing dashboard, and produces a Tier 1 / Tier 2 / Skip greenlight summary.

**Phase 2: Packet build.** For each role you greenlight, identifies the right contact (job poster → hiring manager → 1st-degree → 2nd-degree mutuals), tailors the CV to the JD using a discipline that keeps your identity stable (only the adjacency sentence, one or two highlight cells, and per-role italic context lines change), and drafts channel-appropriate outreach (Connect+Note, longer DM if Open Profile available, InMail as last resort).

**Phase 3: Send.** Walks you through send one role at a time. The plugin opens the right LinkedIn surface, types the message into the field, and stops. You click Send. No autonomous sending.

## Who this is for

People who are:

- Hunting for senior product leadership roles (VP+ scope; 10+ years experience)
- Comfortable editing config files
- Willing to swap in their own CV baseline and configure their own ICP
- OK with a recruiter-grade discipline (peer-to-peer voice, no em dashes, identity-stable CV tailoring)

This plugin is **not** a generic job-search tool. It's tuned for the specific failure modes of executive product search: LinkedIn card data misclassifying roles, ATS staleness, recruiter-masked listings, and the discipline of CV tailoring without rewriting.

## Install

```
/plugin marketplace add github.com/bgolubovski/exec-recruiter
/plugin install exec-recruiter
```

## First-time setup (required)

The plugin ships with placeholder configs. You **must** customize seven things before first use:

1. **`config/icp.yaml`** - your target titles, stage preferences, comp floors, domain preferences
2. **`config/geo-rules.yaml`** - your home city, citizenship/work-auth, and which regions you'll consider
3. **`config/outreach-style.yaml`** - your pattern-match anchors (proof points the outreach drafter references), your sign-off name, your LinkedIn handle, your personal site URL, your CV filename prefix
4. **`config/scoring.yaml`** - the dimension weights for the 1-10 fit score (optional - the defaults are reasonable for senior product roles)
5. **`config/channels.yaml`** - DM / Connect+Note / InMail order, character limits (optional - the defaults are reasonable)
6. **`config/follow-up.yaml`** - Day-5 / Day-7 / Day-10 bump thresholds (optional - the defaults are tested)
7. **`config/ats-sources.yaml`** - ATS domains and query rules for the Google-direct sweep (optional - the defaults cover the 10 main ATSs)

**Replace `templates/cv-baseline.docx`** with your own master CV before first use. The shipped file is a structural stub, not a real CV. See `templates/CV-REQUIREMENTS.md` for the required structure.

After replacing your CV, derive the text-index map (see `agents/cv-tailor.md` Step 3) once and update the agent's example indices to match your CV's structure.

## Configurable surface

Seven config files in `config/` define the user-tunable parts:

- `icp.yaml` - target role titles, search keywords, seniority, sector preferences
- `geo-rules.yaml` - default location, opt-in regions, geo-conditional CV header strings
- `scoring.yaml` - dimension weights for the 1-10 fit score
- `channels.yaml` - DM / Connect+Note / InMail order, credit-preservation rules, character limits
- `follow-up.yaml` - Day-5 / Day-7 / Day-10 thresholds for bumps and final-action
- `outreach-style.yaml` - tone, banned punctuation, sign-off, language, pattern-match anchors, CV filename prefix
- `ats-sources.yaml` - ATS domains, query construction rules, liveness signals, result caps for the Google-direct sweep

## CV baseline

Replace `templates/cv-baseline.docx` with your own master CV. The CV-tailoring discipline preserves your identity blocks (name, headline scaffold, work history dates, education) and only swaps:

1. The headline-positioning fragment
2. The adjacency sentence at the end of the executive summary
3. One or two career-highlight cells (out of six)
4. The italic context line per past role
5. The geo-conditional header

This lets you ship a JD-tailored CV without the false-positive rebuild risk. See `templates/CV-REQUIREMENTS.md` for the full structural spec.

## Skills

| Skill | Triggers on |
|---|---|
| `phase-1-sweep` | "run today's sweep", "Phase 1", "find new roles" |
| `phase-2-packet` | "build packet for X", "tailor CV for X", "Phase 2" |
| `phase-3-send` | "send X", "Phase 3", "ready to send" |
| `score-role` | "score this JD", "is this role a fit" |
| `daily-bump` | "what bumps today", "Day-5 follow-ups" |
| `dashboard-status` | "where do I stand", "today's actions" |

## Agents

- `jd-extractor` - pulls full JDs via the LinkedIn → ATS redirect URL extraction trick (Teamtailor / Workable / Greenhouse / Lever / Ashby / company-careers pages). Solves the LinkedIn-skeleton-view problem. Also handles SPA-based ATSs (Ashby, Workday) via Chrome render for the ATS-Google sweep.
- `ats-google-sweep` - sources roles directly from major ATS domains via Google `site:` queries. Catches roles that never reach LinkedIn. Includes liveness check pre-fetch (~75% of Google-indexed ATS URLs are stale) and ATS-routed body extraction.
- `cv-tailor` - applies the tailoring discipline rules to the CV docx, regenerates PDF via libreoffice.
- `outreach-drafter` - generates Connect+Notes (300 char Premium / 280 standard), longer DMs, and InMail variants per channel preferences.

## Required connectors

| Category | Required for | Options |
|---|---|---|
| Browser | LinkedIn navigation, JD extraction, send-flow positioning, SPA-ATS render | Claude in Chrome MCP |
| Web search | ATS-Google sweep (Step 1B of phase-1-sweep) | WebSearch (built-in) |
| Web fetch | ATS body extraction for static-HTML ATSs | mcp__workspace__web_fetch (built-in) |
| Shell | File ops, libreoffice for PDF generation | Workspace bash (built-in) |
| Contact enrichment (optional) | Better contact identification when 1st/2nd-degree path is unclear | Apollo MCP |
| Calendar (optional) | Scheduled task setup for daily sweep | Cowork scheduled tasks (built-in) |

## Daily workflow

1. Morning: run `/sweep` (or "run today's sweep"). Get a Tier 1 / Tier 2 / Skip summary.
2. Greenlight Tier 1 roles: "build packet for {company}-{role-slug}". Get JD, tailored CV, drafted outreach in `outreach/{slug}/`.
3. Review the packet. Approve.
4. Run `/send {company}-{role-slug}`. The plugin opens LinkedIn, types your message, stops. You click Send.
5. Track follow-ups: `/bump` shows Day-5 to Day-7 windows and Day-10 thresholds.
6. Check `/dashboard` for state of all open roles.

## Send safety

No skill in this plugin sends a LinkedIn message, an email, or an application autonomously. Every send is a two-step: the plugin types into the right field and stops; you click Send. The Phase 3 skill explicitly enumerates the approval gate before each action.

## Memory and state

The plugin keeps no persistent state of its own. Per-role packets live under `outreach/{slug}/` in your project folder. Status, follow-up windows, and inbound signals are tracked in `dashboard.html`. Loss of plugin state never loses your sourcing history.

## License

MIT. See `LICENSE`.

## Contributing

Issues and PRs welcome. The plugin is opinionated about discipline (no em dashes, identity-stable CV, peer-to-peer voice) - those rules are not up for debate. ICP/geo defaults and ATS-source list are open to extension.

## Author

Built by [Blagoja Golubovski](https://github.com/bgolubovski) for personal use, then genericized for sharing. Use at your own discretion; this is not a recruiter-grade service, it's a personal pipeline shared as code.
