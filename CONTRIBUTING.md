# Contributing to exec-recruiter

PRs welcome. A few ground rules:

## Non-negotiables

These are the plugin's discipline, not preferences:

- **No em dashes (—) or en dashes (–) anywhere** - in code, docs, or generated output. Use commas, periods, colons, or restructure.
- **Identity-stable CV tailoring** - the plugin must never rewrite a user's name, dates, titles, employers, bullet points, core competencies, thought leadership, or education sections.
- **No autonomous sending** - every send must be a two-step: the plugin types, the user clicks Send.
- **Peer-to-peer voice in generated outreach** - no banned phrases (passionate, synergy, value-add, thought leader, etc.).

## Welcome PRs

- New ATS domains in `config/ats-sources.yaml`
- New recruiter-masked aggregators in `config/icp.yaml`
- Bug fixes in `scripts/tailor_cv.py` (e.g., handling more XML edge cases)
- New skills that fit the three-phase model
- README clarifications, especially around first-time setup
- Tests for the scoring pipeline

## Not welcome

- Auto-send features
- "Smart rewriter" features that change identity-stable CV fields
- Generic LLM-tone defaults (the discipline is what makes the outreach land)

## Style

- Configuration in YAML, not JSON, where the existing pattern is YAML
- Comments in YAML/Python that explain WHY, not WHAT
- Markdown over HTML where possible
- Keep README sections short; link to references for depth

## Versioning

Semver. Bump in `.claude-plugin/plugin.json`. Tag releases on GitHub.

## Release checklist

Before every commit that touches `.claude-plugin/` or any skill / agent / template:

```bash
./scripts/validate.sh
```

This runs `claude plugin validate` on both `plugin.json` and `marketplace.json`. Fix any reported errors before pushing. The validator's strictness has surprised us before (e.g., the `marketplace.json` `source` field must be `"./"` with the trailing slash, not `"."`), so trust the validator over schemas you find online.

If you update the README in the `.plugin` zip, also update it in the repo — the zip and repo READMEs should stay in sync.
