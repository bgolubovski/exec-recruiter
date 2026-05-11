# CV baseline requirements

The plugin ships with a stub `cv-baseline.docx` showing the required structure.
**Replace it with your own master CV** before first use - the stub is structural,
not personal.

## Required sections (in order)

1. **Name** - your full name, bold, centered, ~20pt
2. **Headline-positioning fragment** - one line just below your name, ~11pt.
   Format: `Chief Product Officer | <positioning-1> | <positioning-2> | <quantifier>`.
   The plugin will replace this per role.
3. **Geo-conditional header** - one line with your location and work-auth status, ~10pt.
   The plugin picks from `geo-rules.cv_header_templates` per role's region.
4. **Contact line** - email, LinkedIn, personal site, ~10pt.
5. **Tailored-for tag** - italic gray line "Tailored for {company}, {role_title}".
   The plugin fills this per role.
6. **EXECUTIVE SUMMARY** - 2-4 sentences. The LAST sentence is the adjacency sentence
   that the plugin rewrites per role to land the role-specific analogue.
7. **CAREER HIGHLIGHTS** - a 2x3 or 3x2 grid of 6 cells. Each cell has a title
   (1-3 words bold) and a body (1-2 sentences). The plugin may modify at most
   2 of 6 cells per role; the other 4 stay fixed.
8. **EXPERIENCE** - each past role has:
    - Company name (bold), role title, dates on the same line
    - One ITALIC context line just below - the plugin rewrites this per target role
    - Bulleted body (3-6 bullets per role) - the plugin NEVER modifies these
9. **CORE COMPETENCIES** - list of 8-15 skills. Plugin never modifies.
10. **THOUGHT LEADERSHIP & RECOGNITION** - talks, articles, awards. Plugin never modifies.
11. **EDUCATION** - degrees, institutions, years. Plugin never modifies.

## What the plugin DOES modify

- Headline-positioning fragment
- Geo-conditional header
- Tailored-for tag
- The adjacency sentence at the end of EXECUTIVE SUMMARY
- 1-2 of 6 CAREER HIGHLIGHTS cells (title + body)
- The italic context line for each role in EXPERIENCE

## What the plugin NEVER modifies

- Your name, email, LinkedIn URL, personal site
- Job titles, employment dates, employer names
- Bullet points under each role (only the italic line above them is tailorable)
- Section headings
- Core competencies list
- Thought leadership content
- Education entries

## Setting `cv_filename_prefix`

Edit `config/outreach-style.yaml` `cv_filename_prefix`. Common pattern:
`"Lastname-Firstname-CV"`. The plugin saves tailored CVs as
`{cv_filename_prefix}-{role_slug}.docx` (and `.pdf`).

## Re-deriving the text-index map

The `cv-tailor` agent uses python to verify replacements landed by reading
specific text indices in the docx XML. Those indices are SPECIFIC TO YOUR CV
structure. After you replace `cv-baseline.docx` with your own, run the script
the agent describes (see `agents/cv-tailor.md` Step 3) once against your
baseline to identify which indices correspond to which fields, then update the
agent's `[1, 2, 8, 10, 12]` example to match your actual mapping.

## Reference PDF

`cv-baseline-reference.pdf` is the PDF render of `cv-baseline.docx`. The plugin
does not use the reference PDF at runtime - it's just for visual sanity-check
of what the docx looks like. After replacing the docx with your own, regenerate
the reference PDF:

```bash
libreoffice --headless --convert-to pdf --outdir templates/ templates/cv-baseline.docx
mv templates/cv-baseline.pdf templates/cv-baseline-reference.pdf
```
