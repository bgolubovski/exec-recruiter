# How to publish this repo to your GitHub

These commands assume you have the GitHub CLI (`gh`) installed and authenticated.
If not: `brew install gh && gh auth login` first.

## One-time setup

```bash
# 1. cd into the unzipped exec-recruiter-v0.3.0 folder
cd ~/path/to/exec-recruiter-v0.3.0

# 2. initialize git
git init -b main
git add .
git commit -m "Initial commit: exec-recruiter v0.3.0"

# 3. create the public repo on your GitHub account
gh repo create exec-recruiter \
  --public \
  --description "Personal executive recruiter for Product Leadership job hunts. Dual sourcing across LinkedIn AND major ATS domains via Google site: search." \
  --homepage "https://github.com/bgolubovski/exec-recruiter" \
  --source=. \
  --remote=origin \
  --push

# 4. tag the v0.3.0 release
git tag -a v0.3.0 -m "v0.3.0: first public release"
git push origin v0.3.0

# 5. create a GitHub release
gh release create v0.3.0 \
  --title "v0.3.0 - First public release" \
  --notes "Genericized release of exec-recruiter. See README.md for setup. Replace templates/cv-baseline.docx with your own CV and edit config/*.yaml before first use."
```

After this, the repo is live at:

  **https://github.com/bgolubovski/exec-recruiter**

## How friends install your plugin

Inside Cowork (or Claude Code):

```
/plugin marketplace add github.com/bgolubovski/exec-recruiter
/plugin install exec-recruiter
```

They'll get the genericized version and need to do their own first-time setup
(replace CV, edit configs).

## How you push updates later

```bash
cd ~/path/to/exec-recruiter-v0.3.0
# make changes
git add .
git commit -m "v0.4.0: <what changed>"

# bump version in .claude-plugin/plugin.json from "0.3.0" to "0.4.0"
# (or whatever the next version is)

git push origin main
git tag -a v0.4.0 -m "v0.4.0: <what changed>"
git push origin v0.4.0

gh release create v0.4.0 --title "v0.4.0" --notes "<changelog>"
```

Friends pick up updates with:

```
/plugin marketplace update
/plugin update exec-recruiter
```

## Important: keep your private install separate

Your locally-installed v0.2.0 with your real configs and CV is at:

```
~/Library/Application Support/Claude/local-agent-mode-sessions/<...>/rpm/plugin_01FaKY5vj2LNBQKo8FGCytQp/
```

This local install **does not change** when you publish v0.3.0 publicly. You
keep using your personal v0.2.0; the public v0.3.0 is for other people.

If you ever want to use the public version yourself:

1. Back up your seven `config/*.yaml` files and your `templates/cv-baseline.docx`
   to a safe folder.
2. Uninstall the local v0.2.0 in Cowork.
3. Install the public v0.3.0: `/plugin marketplace add github.com/bgolubovski/exec-recruiter` then `/plugin install exec-recruiter`.
4. Copy your backed-up configs and CV back into the plugin folder.

## Common questions

**Q: Will my friends see my real configs?**
No. The published v0.3.0 has all placeholders. Your real configs only live in your
local install at `~/Library/Application Support/Claude/.../rpm/plugin_01FaKY5vj2LNBQKo8FGCytQp/`.

**Q: Can I make the repo private?**
Replace `--public` with `--private` in step 3. But then friends can't install via
the marketplace URL unless they have repo access. You'd need to share the
`.plugin` bundle directly, or invite them as repo collaborators.

**Q: What if a friend finds a bug?**
They file a GitHub issue. You fix, bump version in `plugin.json`, push, tag,
release. Everyone updates with `/plugin update exec-recruiter`.
