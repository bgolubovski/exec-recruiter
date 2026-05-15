# Interviewer research patterns

How to research a named interviewer before the call. Sources, depth-of-coverage by altitude, conflict resolution.

## Standard sources, in priority order

1. **LinkedIn profile** (the primary source). Pull: current title, tenure at current company, prior titles + companies most-relevant-first, education, certifications, posts about the company in the last 90 days, mutual connections if visible.
2. **TheOrg.com profile** (`theorg.com/org/<company>/org-chart/<person-slug>`). Often has structured bio + manager + team. Useful for org-chart placement and for catching title-conflict signals.
3. **Crunchbase Person profile**. Funding-round commentary, advisory positions, prior company exits.
4. **Personal site / blog / GitHub**. Optional but high-signal for technical interviewers.
5. **Conference + podcast appearances**. Search `"<name>" speaker OR podcast OR keynote` for the last 24 months.
6. **Company press releases mentioning them**. Search `"<name>" "<company>" 2026 OR 2025` for hire announcements, promotion notes, launch quotes.
7. **Twitter / X account**. Last 30 days of activity if the account is active. Especially useful for founders / CEOs.
8. **Glassdoor / Repvue mentions** (occasional; rare to find specific names but useful for company climate).

## Depth by altitude

### Recruiter / Talent screener

Minimum depth:
- LinkedIn URL + title
- Confirm they're at the company (not a contracted external recruiter unless that's the channel)
- Note any prior tenure at recruiting firms or in-house TA roles

Skip:
- Personal site, GitHub, conference appearances

### Peer / hiring manager

Standard depth:
- LinkedIn full career arc most-relevant-first
- Education with school + degree + years
- Last 90 days of LinkedIn activity (posts about the company / product)
- TheOrg placement
- Cross-reference for title conflicts

Skip:
- Personal site (unless they're an active blogger)
- GitHub (unless they're CTO / Eng-track)

### Founder / CEO

Maximum depth:
- All of the above
- Press coverage (last 12 months minimum)
- Funding round commentary and what they said publicly during raises
- Conference talks + podcast appearances + Wikipedia entry if it exists
- Academic background if relevant (e.g., research-PhD-turned-founder with notable-academic-collaborator publication trail)
- Twitter / X activity, especially product-philosophy threads

For founder calls, depth on background matters enormously. Don't bring "we've raised $X" facts unless you can also bring "and you said in that interview that the hardest part was Y."

### Incumbent in the same seat / sibling VP

Standard depth + extra emphasis on:
- Their tenure-in-seat (how long they've been doing the job you're interviewing for)
- Their prior employer + role (what shape they'd bring as a peer)
- Any conference talks or blog posts about HOW they think about product
- Public references to their team's recent work (launches, customer wins, hires)

## Conflict resolution

### Title conflicts across sources

Common pattern: LinkedIn says VP Product, TheOrg says Head of Product, company website says Director of Product. This is typical when titles change without all public records updating in sync.

Resolution:

1. Trust LinkedIn first for current title.
2. Surface the conflict in the prep packet explicitly: "LinkedIn: VP Product. TheOrg: Head of Product. Likely recent promotion - confirm in call."
3. Use the conflict as part of the disambiguation question.

The Sam Carter case is the canonical example. LinkedIn + TheOrg both showed VP Product; an older bio still said Head of Product. The conflict pointed at recent promotion, which connected to the "first product leader" JD ambiguity.

### Tenure / role-overlap conflicts

Sometimes LinkedIn shows overlapping roles (e.g., concurrent Director of X + Advisor to Y). Note both. Don't make assumptions about which is primary.

### Multiple people with same name at same company

The skill should NOT auto-pick. Surface all matches and ask the user to confirm which profile.

### LinkedIn profile inaccessible (private profile, paywall, login-required)

Pull what's available from Google cache, Bing, DuckDuckGo. If still gated, note "LinkedIn profile not publicly accessible; relying on company-website bio + TheOrg + press coverage." Generate prep based on lower-confidence intel and surface the gap.

## What NOT to use as research signal

- **Photo / appearance**: skip entirely
- **Personal life / family / location specifics beyond city**: skip
- **Old non-work social posts**: skip
- **Political affiliations**: skip
- **Anything that would feel creepy or excessive if the interviewer saw your research dump**: skip

The packet's interviewer profile section should pass the "could I show this to the interviewer without embarrassment" test.

## Anchor surfacing

The research should always surface 2-3 things in the interviewer's profile that map to specific user anchors. Examples from canonical cases:

- Sam Carter: payments-PM-at-fintech-A + payments-SPM-at-fintech-B = consumer-fintech-payments depth → user's Atlas / Quanta Pay anchor lands instantly
- Non-CS-degree judgment-oriented background + self-taught ML upskilling = user should lean on operating-model framing rather than deep ML theory
- Research-PhD-turned-founder with notable-academic collaborator → first-principles thinker → user should compress framework language and lead with rigorous reasoning

When two or three anchor-mapping signals can be surfaced cleanly, the packet's "Tier 1 anchors in this order" section becomes easy to write. When the anchor-mapping is thin, the packet should flag that the call needs more discovery before the user's strongest anchors will land.

## Output to the packet

For each interviewer researched, the packet writes:

1. Header: name + LinkedIn URL + current title + location + reports-to inferred
2. Career arc (most-relevant-first, 5-7 bullets max)
3. Education (school + degree + years)
4. Notable certifications or technical signals
5. "Signals to probe and use" - 3-5 specific things in their background that map to user anchors
6. "Signals to avoid" - 1-3 things where over-claiming or wrong framing would backfire
7. Title conflicts, if any
8. Reading note: a 1-2 sentence operating thesis on how to communicate with them (e.g., "First-principles thinker, won't tolerate framework-heavy MBA-speak. Lead with rigorous reasoning, not buzzwords.")

See the Sam Carter example in `outreach/{slug}/prep-sam-meeting.md` for the canonical shape.
