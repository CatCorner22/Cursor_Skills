# How to get all 189 skills into Cursor

`all-skills` is a **plugin**, not a skill. **Customize → Skills** lists skill names (`nextjs`, `proactive-agency`, `huggingface-best`, …). It will never show a row titled `all-skills`. That name appears under **Customize → Plugins** after you import this repo as a marketplace (step 1) and install the plugin (step 2).

## 1. Import this repo as a marketplace

Cursor does not auto-install plugins just because the folder is on disk. You have to import the repository once.

1. Open [cursor.com/dashboard](https://cursor.com/dashboard) → **Plugins & MCPs**.
2. Under **Team Marketplaces**, click **Add Marketplace** → **Import from Repo**.
3. Paste `https://github.com/CatCorner22/Cursor_Skills`.
4. If asked for a branch, use `cursor/skills-plugins-second-review-cc2b` until that PR is merged to `main`.
5. In the plugin list, add **`all-skills`** (and any pack plugins you want).
6. Save. Optionally set **`all-skills`** to **Default On** so it installs for you automatically.

On a personal (non-team) plan, use Customize in the desktop app → **From GitHub Repository** and paste the same URL.

## 2. Install the plugin in the app

1. Open the **Cursor desktop app** (not only a Cloud Agent chat).
2. Open **Customize** in the sidebar.
3. Open the **Plugins** section (not Skills).
4. Search **`all-skills`**.
5. Click **Install** (user or project scope).
6. Command Palette → **Developer: Reload Window**.

## 3. Confirm the skills (not the plugin name)

1. Customize → **Skills**.
2. Set the filter to include **Workspace** and **User** (not Team-only).
3. Search for a known skill: `proactive-agency`, `nextjs`, or `huggingface-cli`.
4. You should see ~189 Agent Decides skills. Type `/` in Agent chat to search the same list.

## If you only opened this repo as a folder

Project skills live in `.cursor/skills/` on **this branch**. Customize → Skills, filter **Workspace**, then search `nextjs`. You still will not see the word `all-skills` there.

If those workspace skills are missing, the folder you opened is probably `main` (this plugin does not exist on `main` yet). Checkout:

```bash
git fetch origin cursor/skills-plugins-second-review-cc2b
git checkout cursor/skills-plugins-second-review-cc2b
```

Then Reload Window.

## Cloud Agent chats

The Cloud Agent Skills pop-out is **not** Customize → Skills. It shows skills already attached to that run. Importing the marketplace and setting **`all-skills`** to **Default On** / **Required** is what makes the next Cloud Agent run see them. This chat cannot refresh its own list.
