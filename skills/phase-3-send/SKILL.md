---
name: phase-3-send
description: Walk through Phase 3 send for a single greenlit packet. Triggers on "send X", "Phase 3 X", "/send X", "fire X", "let's send X", or "ready to send X". Opens the right LinkedIn surface for each channel (Connect+Note dialog, DM thread, InMail compose), types the drafted message into the field, and stops with the cursor positioned for the user to click Send. Never sends autonomously. Walks the user through each channel in priority order; after each user-confirmed send, updates the dashboard from "drafted" to "pending" with sendDate today.
---

# phase-3-send

Walk the user through Phase 3 send for one role at a time. Position the browser, type the message, stop. The user clicks Send.

## When to invoke

The user says: "send X", "Phase 3 X", "/send X", "fire X", "let's send X", "ready to send X". X is a slug or company name.

## Critical safety rule

**No skill in this plugin sends a LinkedIn message, an email, or an application autonomously.** This skill ALWAYS:

1. Types the message into the field
2. Stops with the cursor positioned
3. Tells the user to click Send themselves
4. Waits for the user's "sent" reply before moving to the next channel

If the user types `send` or `next` after seeing the typed message, the skill moves to the next channel. If the user wants to edit, the skill waits.

## Workflow

### Step 1: Resolve the packet

The user names a role. Look up:

- `outreach/{slug}/outreach.md` for the drafts
- `outreach/{slug}/jd.md` for the JD context
- The dashboard ROLES entry for status, contacts, channels

If the packet's status is not "drafted", confirm with the user before proceeding. (E.g., already-sent packets shouldn't be re-fired.)

### Step 2: Confirm the send plan

Echo back the drafts and the channel plan. Ask the user to confirm:

- Primary channel + contact
- Backup channel + contact (if any)
- Application path (Workable, Teamtailor, Greenhouse, Lever, careers page, Easy Apply)
- InMail credit decision (preserve / spend - default preserve)

### Step 3: Apply via ATS first (parallel to outreach)

If there's an application URL, navigate to it FIRST. The application can submit while the user is reviewing/sending Connect+Notes - parallel work.

For Workable / Teamtailor / Greenhouse / Lever / Ashby / company-careers:

1. Navigate to the apply URL
2. If the form has an Autofill option (Workable's "Import resume from..."), use it to seed personal info
3. Upload the tailored CV PDF (use `mcp__Claude_in_Chrome__file_upload` with the file input ref)
4. Fill required fields (First name, Last name, Email, Phone)
5. Paste the Summary text into the optional Summary box (drawn from `outreach.md` cover-letter angle)
6. If the JD has an anti-bot screener word, ensure it appears in a free-text field
7. STOP at Submit. Tell the user to click Submit.

### Step 4: Connect+Note flow (per channel in priority order)

For each contact in the channel plan, in order:

1. Navigate to the contact's LinkedIn profile (`https://www.linkedin.com/in/{slug}/`)
2. Check the contact state:
   - 1st-degree: Message button -> open thread, type DM
   - 2nd-degree with Open Profile: Message button (verify it doesn't paywall to InMail; click and check the result)
   - 2nd-degree without Open Profile: Connect path via More -> Connect -> Add a note
3. For Connect+Note path:
   a. Click `More`
   b. Click `Connect`
   c. In the dialog, click `Add a note`
   d. Click into the textarea
   e. Type the Connect+Note (Premium = 300 char, standard = 280 char)
   f. Confirm char count is within limit
   g. STOP. Tell user "Send is active. Click it when ready."
4. Wait for user "sent" or "next" reply before navigating to the next contact

### Step 5: InMail flow (only if no free path exists)

InMail is the channel of last resort. Before any InMail send:

- Confirm the user wants to spend a credit on this role (per `channels.inmail_credits`)
- Confirm the user has credits available
- Confirm there's no Open Profile or Connect+Note path (re-check)

If approved:

1. Navigate to the contact profile
2. Click Message
3. The InMail upgrade dialog appears - close it
4. Use the Message dialog (sometimes available even without Premium for certain Open Profile users)
5. If only InMail is available, the user must explicitly approve the credit burn before the type-and-stop step
6. Type the InMail (longer, 150-220 words)
7. STOP

### Step 6: Update dashboard

After each user-confirmed send:

1. Append a `sent` entry to `outreach/{slug}/outreach.md` under "Send log" with timestamp, channel, contact name
2. Move the dashboard ROLES entry from `status: "drafted"` to `status: "pending"`
3. Set `sendDate: "{today_yyyy_mm_dd}"`
4. Update `channels` array with what was actually sent
5. Set `sendName` to a short identifier like "primary-and-backup" or "single-contact"
6. Update the role's `note` field with the send log

### Step 7: Set follow-up watch

After all channels for the role are sent, calculate the follow-up dates per `${CLAUDE_PLUGIN_ROOT}/config/follow-up.yaml`:

- Day 5: bump window opens
- Day 7: bump window closes
- Day 10: final action threshold

Append these to the role's `outreach.md` as a "Follow-up watch" section.

### Step 8: Confirm done

Output a tight summary in chat:

- Channels sent (with timestamps)
- 0 InMail credits burned (or note if any)
- Follow-up dates set
- Computer:// link to outreach.md

## Approval gate (before the FIRST type-and-stop)

Confirm with the user one last time:

- [ ] CV attached/uploaded?
- [ ] Outreach drafts reviewed?
- [ ] Channel plan confirmed (primary + backup contacts)?
- [ ] Comfortable with positioning angle (e.g., "three-time CPO going IC by choice" for an unusual role)?
- [ ] Comp expectations clear?

The user's `send X` command is greenlight for the workflow but each individual click stays the user's. Type and stop.

## Failure modes to watch

- **Open Profile paywalls at send time**: the Message button shows but clicking it triggers an InMail upgrade dialog. Close, fall back to Connect+Note via More -> Connect path. Reset the channel plan for that contact.
- **Profile slug 404**: the LinkedIn URL extracted from a search result is sometimes wrong. Re-search for the contact's name + company to recover the actual URL.
- **Connect button missing on 2nd-degree**: some 2nd-degree profiles hide Connect under More -> Connect (especially after the user has viewed before). Always check More menu.
- **Workable Autofill conflicts**: Autofill can overwrite manually-typed personal info. Either Autofill first then check, or skip Autofill and type manually.
- **JD-required screener word missing from final application**: scan the application form one more time before Submit to make sure any anti-bot words appear in a visible free-text field.

## Send safety

- Never click Send / Submit / Post / Publish autonomously
- Never forward a connection request without the user's explicit "send"
- Never paste a draft and then click - paste and stop
- Always show the message verbatim in chat before typing
- Always show char count to confirm under the limit before typing
- Always confirm the message is in the right field before stopping
