---
name: score-role
description: "Score a single role against the user's ICP and scoring weights. Triggers on \"score this role\", \"score this JD\", \"is this a fit\", \"rate this\", \"/score\", or pasting a JD URL with no other context. Pulls the JD body if needed, applies dimensional scoring per scoring.yaml, returns a 1-10 score with per-dimension breakdown and tier classification. Lightweight, no packet generation."
---

# score-role

Score one role against the user's ICP. No packet build. Just the score, the rationale, and the tier.

## When to invoke

The user pastes a JD URL with no other context, or says "score this", "is this a fit", "rate this role", or "/score X". Useful for one-off triage of inbound roles (recruiter pings, network referrals) without invoking the full Phase 1 sweep.

## Workflow

### Step 1: Get the JD

If the user provides a LinkedIn jobs URL, pull the full body via the ATS-redirect trick (delegate to `jd-extractor`). If the user pastes JD text directly, use that.

### Step 2: Extract signals

Parse for:

- Title (and whether it matches `icp.target_titles`)
- Company stage (Series A-D, post-IPO, public)
- Domain / sector
- Reporting line (CEO / CTO / CPTO / other)
- Org scope implied (size of product team, scope of remit)
- Comp band if stated
- Geo + modality (Remote / Hybrid / On-site, days in office)
- Anti-pattern signals: IC framing, specialist domain expertise required, narrow scope, recruiter-masked

### Step 3: Apply dimensional scoring

Per `${CLAUDE_PLUGIN_ROOT}/config/scoring.yaml`, score each dimension 1-10:

- **stage**: weight 0.20
- **domain**: weight 0.20
- **scope**: weight 0.15
- **comp**: weight 0.10
- **geo**: weight 0.10 (binary - hard filter)
- **founder_quality**: weight 0.10
- **ai_native_signal**: weight 0.10
- **founder_partnership**: weight 0.05

Final score = sum(weight * dimension_score).

### Step 4: Apply hard blockers

If any `scoring.hard_blockers` apply, zero out the role: clearance requirements not held, on-site only outside relocation regions, sub-Series-A, title is product-marketing/PR/regulation, hybrid 5-days outside home metro.

### Step 5: Apply post-JD-extraction checks

- Explicit IC framing -> downgrade by 1 tier
- FCA-specialist or other domain-specialist demand the user doesn't have -> downgrade by 1 tier
- Founder's Associate / Chief of Staff scope in JD body -> downgrade by 1 tier

### Step 6: Triage and report

Output:

- Final score (1-10, one decimal)
- Per-dimension breakdown (which dimensions raised vs lowered the score)
- Tier classification: Tier 1 / Tier 2 / Skip (per `scoring.tier_*_threshold`)
- Friction flags
- Recommendation: greenlight for Phase 2 / surface friction for user call / skip with reason

If the role is a strong Tier 1, offer to proceed to Phase 2 (build the packet). If Tier 2, offer the friction-flag list for the user to make the call. If Skip, output the one-line reason.

## Output discipline

Tight. No em/en dashes. No trailing summaries. Per-dimension breakdown as a one-line each, not a table.

Format:

```
Score: 7.5 (Tier 1)

Stage 9 (Series B, GV-backed) | Domain 8 (AI-native B2B) | Scope 8 (VP, reports to CTO, sits on SLT)
Comp 6 (not stated, UK band ~£180K implied) | Geo 10 (UK Remote, fits) | Founder 8 (Dev Amratia, AI advisor)
AI signal 9 (ML-trained on $2T schedules, AI-first ops) | Founder partnership 7 (CTO-led, founder-led ambiguity)

Friction: UK-based with travel to Shoreditch office; ATS body wants AI-native operating model owner.

Recommendation: greenlight Phase 2.
```
