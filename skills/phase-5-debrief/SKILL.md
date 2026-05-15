# phase-5-debrief

Process post-call notes from a meeting prepared via phase-4-prep. Capture the intel learned in the call, update the dashboard, identify the next-action, and route to the right next step (Phase 4 again for next round, Phase 3 for additional outreach, mark replied / advanced / rejected, etc.).

## When to invoke

The user says: "debrief X", "log my call with X", "/debrief X", "/debrief <slug>", "I just talked to <name>, here are my notes", or pastes call notes / a transcript with no other framing.

User-invoked only. Never auto-fires.

## Inputs

- `slug` - the role slug (required)
- `interviewer_name` - who the user just spoke with (required if more than one prep packet exists for the role)
- `notes` - free-form call notes / takeaways / transcript / raw thoughts the user types in (required)
- `next_action_hint` - optional user hint: "they want to advance", "they're scheduling next round", "they want references", "they're going to come back to me", "I should pass", etc.

If the user invokes without notes, prompt for them.

## Workflow

### Step 1: Read role context

Read `dashboard.html` for the role's current state. Read `outreach/{slug}/prep-{interviewer-slug}-meeting.md` if it exists — the prep packet's predictions and friction flags will help structure the debrief.

### Step 2: Parse the user's notes

Extract:

- **Who said what**: especially scope answers, comp signals, timeline signals, next-step commitments
- **What surprised the user**: where the call's reality diverged from the prep's expectations
- **Org / scope clarity**: did the scope-disambiguation question get answered? Above / beside / backfilling / different from all three?
- **Comp signals**: any band surfaced by them, any range mentioned by user
- **Process signals**: next round, panel composition, reference-check timing, decision timeline
- **Friction signals**: anything they pushed back on, anything they probed harder than expected
- **Positive signals**: anything they responded warmly to, any anchor that landed especially well
- **Negative signals**: anything that landed flat, any anchor that backfired

### Step 3: Structure a debrief artifact

Save `outreach/{slug}/debrief-{interviewer-slug}.md` covering:

- Header: who, when, format (matching the prep packet header)
- Outcome read: positive / neutral / negative / unclear
- Scope answer (if surfaced) - the disambiguation question's actual answer
- Comp signals captured
- Process / next-step commitments
- Anchors that landed
- Anchors that didn't land
- New friction flags surfaced
- New positive signals surfaced
- Anything to remember for the next round (if there is one)
- Raw notes section (preserve user's original notes verbatim)

### Step 4: Update the dashboard

For the role's entry:

- If outcome was positive AND a next-round meeting is committed: status stays `active`, add the next meeting + interviewer to `channels`, suspend bump watches.
- If outcome was positive but no next-round committed yet: status `active`, set a 5-day follow-up watch; if no movement by Day 5, draft a polite check-in.
- If outcome was "they want to come back to me with a decision in N days": status `active`, set a check-in watch at day N+2.
- If outcome was a clean advance to a structured next stage (e.g., "they want references" or "next round is panel on Date X"): status `active`, log next-stage trigger.
- If outcome was "they're going to pass" or "doesn't seem like a fit": status `rejected` with a debrief note capturing why.
- If outcome was ambiguous: status stays as it was, surface the ambiguity to the user with an explicit follow-up question.

Update the role's note with a one-line summary of the debrief + reference to the debrief file path.

### Step 5: Identify and surface the next-action

Based on the debrief, present the user with:

- **Next-action recommendation**: one of `prep-next-round`, `send-thank-you-and-wait`, `send-requested-materials`, `passive-watch`, `mark-rejected`, `escalate-to-different-contact`
- **One-line rationale**
- **Concrete next step the user should take in the next 24-48 hours**

If `prep-next-round` is recommended: offer to invoke phase-4-prep for the next interviewer, OR (if user knows the name) hand off cleanly to that skill.

If `send-thank-you-and-wait` is recommended: note that Phase 5 does NOT draft outreach (per design). Refer user to manual outreach drafting if they want a thank-you.

### Step 6: Update memory if a pattern is learned

If the debrief surfaces something that contradicts or extends an existing memory file (e.g., a new rejection pattern, a new positive-signal type, a new altitude-specific behavior), surface it and ask the user if they want to log it to memory.

Examples worth surfacing:
- Profile-view-not-positive-signal patterns (already in `feedback_profile_view_signal.md`)
- Recruiter-masked auto-screen patterns (already in `feedback_recruiter_masked_rejects.md`)
- Crypto-native rejection patterns (already in `feedback_crypto_native_rejects.md`)
- New patterns: domain-specialist rejections at FTSE-100 direct employers (e.g., [sample-asset-manager]-class FCA-regulated specialist gating), warmer-than-expected founder reads at first-call, etc.

Don't auto-write memory. Always ask the user first.

### Step 7: Present in chat

Output:

- Headline: outcome read (1-2 words), with the most important fact from the debrief
- Scope answer captured (if it was the call's load-bearing moment)
- Comp signal captured (if any)
- Next-action recommendation with rationale
- Concrete next step in 24-48 hours
- Computer-link to the saved debrief file
- If memory-worthy, a flagged "consider logging to memory" prompt

### Step 8: STOP

Do NOT auto-trigger phase-4-prep for a next round. Do NOT auto-draft outreach. The user decides the next step.

## Approval gates

- Before updating status from `active` to `rejected`, confirm with the user. Rejections are sticky.
- Before suspending bump watches, surface the change explicitly so the user knows the cadence is paused.
- Before flagging anything for memory, ask the user. Memory writes are permanent across sessions.

## Failure modes

- **User notes are sparse or one-line**: surface what's captured, ask for missing dimensions (scope answer? comp signal? next step?).
- **Notes contradict the prep packet's predictions**: surface the divergence explicitly. Don't smooth it over.
- **Notes describe a meeting that doesn't match any prep packet on file**: ask whether this was an unprepped call or a different role. Don't auto-create a debrief without a role match.
- **User describes outcome ambiguity ("I don't know if they liked me")**: surface the ambiguity, do not classify outcome as positive or negative. Recommend a passive-watch + Day-5 check-in.

## Output discipline

- No em or en dashes anywhere (per `outreach-style.yaml`).
- Vector / Compass distinction respected (per memory).
- Be honest about ambiguity — false-positive reads are worse than no read.
- Don't draft outreach (per Phase-4/5 scope decision).

## References

- See `outreach/{slug}/prep-sam-meeting.md` for the canonical prep-packet shape Phase 5 debriefs against.
- See `feedback_profile_view_signal.md` for the canonical example of a debrief-driven memory write.
- Phase 4 = pre-call (prep). Phase 5 = post-call (debrief). They pair as a unit. Phase 4's predictions are the calibration baseline Phase 5 grades against.
