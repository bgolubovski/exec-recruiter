# ATS-Google query recipes

Canonical Google `site:` query patterns for the ATS-Google sweep (Step 1B of phase-1-sweep). Used by the `ats-google-sweep` agent.

## Core query template

```
site:{ATS_DOMAIN} ({TITLE_OR_LIST}) ({GEO_OR_LIST}) -intern -junior -associate -internship after:{TODAY_MINUS_14_DAYS}
```

Constraints:
- 32-word ceiling, ~2,048-char ceiling
- Use `OR` for alternates within a parenthesised group
- Use `-term` to exclude
- `after:YYYY-MM-DD` biases toward freshly indexed pages (does not eliminate stale URLs - liveness check still required)

## Per-region examples

### UK

```
site:boards.greenhouse.io ("VP Product" OR "Chief Product Officer" OR "Head of Product") ("London" OR "United Kingdom") -intern -junior -associate after:2026-04-26
```

```
site:jobs.lever.co ("VP Product" OR "Chief Product Officer" OR "Head of Product") ("London" OR "United Kingdom") -intern -junior -associate after:2026-04-26
```

```
site:jobs.ashbyhq.com ("VP Product" OR "Chief Product Officer" OR "Head of Product") ("London" OR "United Kingdom") -intern -junior -associate after:2026-04-26
```

### US-remote

```
site:boards.greenhouse.io ("VP Product" OR "Chief Product Officer" OR "Head of Product") ("Remote" OR "United States" OR "USA") -intern -junior -associate after:2026-04-26
```

```
site:myworkdayjobs.com ("VP Product" OR "Chief Product Officer" OR "Head of Product") ("Remote" OR "United States") -intern -junior -associate after:2026-04-26
```

### EU

```
site:jobs.ashbyhq.com ("VP Product" OR "Chief Product Officer" OR "Head of Product") ("Berlin" OR "Amsterdam" OR "Madrid" OR "Paris" OR "Dublin" OR "Lisbon") -intern -junior -associate after:2026-04-26
```

## Per-ATS liveness signals

Pilot data: Google's index lags ATS reality by days-to-weeks. Roughly 75% of Google-indexed ATS URLs are stale (filled or pulled). Always run liveness check before fetching the body.

| ATS | Stale signal | Detection |
|---|---|---|
| Greenhouse | Redirect to `/{org}?error=true` | URL contains `?error=true` after redirect |
| Lever | Empty response body | Body length under 200 bytes |
| Workday | 404 status or no role title | HTTP 404 or `<title>` lacks role title |
| iCIMS | Redirect to `/search` | URL contains `/search` after redirect |
| Jobvite | Empty response body | Body length under 200 bytes |
| BambooHR | Redirect to `/search` | URL contains `/search` after redirect |
| SmartRecruiters | 404 or empty role | HTTP 404 or `<title>` lacks role title |
| Workable | Redirect to `/search` | URL contains `/search` after redirect |
| Teamtailor | 404 or empty role | HTTP 404 or `<title>` lacks role title |
| Ashby | SPA shell | Body contains `"You need to enable JavaScript"` -> route to jd-extractor (Chrome) |

## Body-extraction routing

| ATS | Extraction path |
|---|---|
| Greenhouse | `web_fetch` (static HTML) |
| Lever | `web_fetch` (static HTML) |
| Workday | `jd-extractor` agent (JS render) |
| iCIMS | `web_fetch` |
| Jobvite | `web_fetch` |
| BambooHR | `web_fetch` |
| SmartRecruiters | `web_fetch` |
| Workable | `web_fetch` |
| Teamtailor | `web_fetch` |
| Ashby | `jd-extractor` agent (SPA, needs Chrome) |

## Recruiter-aggregator hot spots

These hosts on each ATS heavily over-index in `site:` results and should auto-Skip per `icp.recruiter_masked_known_aggregators`:

- **Lever**: `jobs.lever.co/jobgether/*` (Jobgether posts dozens per week)
- **Greenhouse**: `boards.greenhouse.io/burnssheehan/*`, `boards.greenhouse.io/aretigroup/*`
- **Ashby**: `jobs.ashbyhq.com/SignalFire/*` (VC-talent-network listings; on-ICP but mediated; flag, do not auto-skip)

## When the title cluster is too long

If `("VP Product" OR "Chief Product Officer" OR "Head of Product" OR "VP of Product" OR "VP Products" OR "SVP Product" OR "SVP of Product")` plus geo terms breaks the 32-word limit, split into two queries:

Query A (CPO + VP cluster):
```
site:{DOMAIN} ("Chief Product Officer" OR "VP Product" OR "VP of Product" OR "VP Products") ({GEO}) -intern -junior -associate after:{DATE}
```

Query B (SVP + Head cluster):
```
site:{DOMAIN} ("SVP Product" OR "SVP of Product" OR "Head of Product") ({GEO}) -intern -junior -associate after:{DATE}
```

## Result caps

Per `ats-sources.yaml result_caps`:
- 5 results per query (deliberately tight; pilot showed high staleness)
- 25 results per ATS per sweep
- 100 results absolute ceiling per sweep

If approaching the ceiling, prioritize: Greenhouse > Ashby > Lever > Workable > Teamtailor > others.
