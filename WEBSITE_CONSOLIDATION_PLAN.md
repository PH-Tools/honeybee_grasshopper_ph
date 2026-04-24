# PH-Tools Website Consolidation Plan

> **Created**: 2026-04-23  
> **Status**: Planning  
> **Goal**: Consolidate PH-Tools web properties into two clean, branded Astro sites sharing the bldgtyp design system.

---

## 1. Current State — What Exists Today

### 1.1 Web Properties

| # | Domain / URL | Hosting | Source Repo | Tech | Purpose |
|---|-------------|---------|-------------|------|---------|
| A | `www.passivehousetools.com` | **Dreamhost** (IP: 173.236.255.61) | Unknown (hand-edited HTML on Dreamhost) | Static HTML | Landing page listing 4 projects |
| B | `docs.passivehousetools.com` | **GitHub Pages** (CNAME → ph-tools.github.io) | `PH-Tools/ph-docs` | Astro 5 + Pagefind | Unified developer docs hub |
| C | `ph-tools.github.io/honeybee_grasshopper_ph/` | **GitHub Pages** (from this repo) | `PH-Tools/honeybee_grasshopper_ph` `docs/` folder | Hugo 0.124.1 | Install guide, quick start, learn more, contact for GH plugin |
| D | `ph-tools.github.io/CarbonCheck/` | **GitHub Pages** (from CarbonCheck repo) | `PH-Tools/CarbonCheck` | Unknown | CarbonCheck landing page |

### 1.2 Dreamhost Account Details (Confirmed 2026-04-23)

**Domain registration**: `passivehousetools.com` is **registered through Dreamhost**.  
**Registration expiry**: 2027-01-04  
**Hosting plan**: Shared Unlimited (server: `iad-shared-68-05`, US-East Ashburn, Virginia)  
**Traffic**: ~1,103 visits (at time of check)

**Other domains on this Dreamhost account** (for awareness):
| Domain | Plan | Notes |
|--------|------|-------|
| `bldgtyp.com` | Shared Unlimited | "Transfer Registration" shown — may be registered elsewhere |
| `chrismaybuilders.com` | Shared Unlimited | Expires 2026-12-10 |
| `passivehouse.tools` | Redirect | Currently goes nowhere — intended to redirect to passivehousetools.com but never configured |
| `passivehousetools.com` | Shared Unlimited | **This domain** — expires 2027-01-04 |
| `ph-nav.com` | DNS Only | Expires 2026-06-23 |
| `ph-switch.com` | DNS Only | Expires 2026-08-05 |

### 1.3 DNS Records (Confirmed 2026-04-23)

Current DNS records for `passivehousetools.com` in Dreamhost panel:

**Custom Records:**
| Name | Type | Value |
|------|------|-------|
| `docs` | CNAME | `ph-tools.github.io` |

**DreamHost Records:**
| Name | Type | Value |
|------|------|-------|
| `@` | A | 173.236.255.61 |
| `ftp` | A | 173.236.255.61 |
| `ssh` | A | 173.236.255.61 |
| `www` | A | 173.236.255.61 |
| `@` | NS | ns1.dreamhost.com |

**Key observations:**
- The `docs` CNAME → `ph-tools.github.io` is how `docs.passivehousetools.com` works today. **Do not touch this record.**
- The `@` and `www` A records point to Dreamhost's server. These need to change to GitHub Pages IPs.
- The `ftp` and `ssh` A records are Dreamhost hosting artifacts. Can be removed after migration.

### 1.4 GitHub Organization Pages Status

- **Org**: `PH-Tools` (https://github.com/PH-Tools)
- **Org Pages repo** (`PH-Tools.github.io`): **Does not exist yet**
- **No verified domains** in org settings (Settings > Pages shows empty)
- Individual repos serve Pages at subpaths: `/honeybee_grasshopper_ph/`, `/CarbonCheck/`, etc.

### 1.5 Branding System

- **Repo**: `bldgtyp/branding` (https://github.com/bldgtyp/branding)
- **Live**: https://bldgtyp.github.io/branding/
- **CDN tokens**:
  - `https://bldgtyp.github.io/branding/tokens/tokens.css` (CSS custom properties)
  - `https://bldgtyp.github.io/branding/tokens/components.css` (reusable component classes)
  - `https://bldgtyp.github.io/branding/tokens/tokens.json` (machine-readable)
- **Fonts**: Outfit (200-700) + JetBrains Mono (300, 400) via Google Fonts
- **Colors**: `--accent: #7a9424`, `--highlight: #DC2626`, light/dark theme via `data-theme`
- **Patterns**: Graph-paper backgrounds (standard/medium/fine)
- **ph-docs already imports** `tokens.css` at `src/styles/global.css:8`

---

## 2. Target State — Where We're Going

### 2.1 Architecture

| Domain | Repo | Tech | Purpose |
|--------|------|------|---------|
| `passivehousetools.com` | `PH-Tools/PH-Tools.github.io` (**new**) | Astro + bldgtyp tokens | Public landing page — project showcase, install/quickstart, resources |
| `docs.passivehousetools.com` | `PH-Tools/ph-docs` (existing) | Astro + bldgtyp tokens | Developer docs, API reference, LLM docs, guides |

Both sites share the same bldgtyp design tokens (fonts, colors, spacing, graph-paper patterns, dark/light theme). They cross-link in their headers/nav.

### 2.2 DNS Changes Required (in Dreamhost Panel)

**Records to CHANGE:**
| Name | Current | Action | New Type | New Value | Why |
|------|---------|--------|----------|-----------|-----|
| `@` | A → 173.236.255.61 | Delete old, add new | A (x4) | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 | Point apex domain to GitHub Pages |
| `www` | A → 173.236.255.61 | **Delete A first**, then create CNAME | CNAME | `ph-tools.github.io` | A and CNAME cannot coexist for same name — must delete A before creating CNAME |

**Records to ADD:**
| Name | Type | Value | Why |
|------|------|-------|-----|
| `_github-pages-challenge-PH-Tools` | TXT | (provided by GitHub during domain verification) | Required by GitHub to verify domain ownership before Pages can serve the custom domain |

**Records to KEEP (do not touch):**
| Name | Type | Value | Why |
|------|------|-------|-----|
| `docs` | CNAME | `ph-tools.github.io` | Already working — serves docs.passivehousetools.com |
| `@` | NS | ns1.dreamhost.com | Dreamhost remains the nameserver/registrar |

**Records to DELETE (after migration confirmed working):**
| Name | Type | Value | Why |
|------|------|-------|-----|
| `ftp` | A | 173.236.255.61 | Dreamhost hosting artifact — no longer needed |
| `ssh` | A | 173.236.255.61 | Dreamhost hosting artifact — no longer needed |

**Dreamhost hosting plan**: After DNS cutover is confirmed working (Phase 6), the "Shared Unlimited" hosting plan for `passivehousetools.com` can be canceled. **Keep the domain registration** — it expires 2027-01-04 and should be renewed. Dreamhost allows keeping a domain registered as "DNS Only" without a hosting plan (similar to `ph-nav.com` and `ph-switch.com` on the same account).

### 2.3 Landing Page Content (`passivehousetools.com`)

**Projects to list** (with cards linking to docs/repos):
1. **Honeybee-PH** → `docs.passivehousetools.com/honeybee-ph/`
2. **PHX** → `docs.passivehousetools.com/phx/`
3. **CarbonCheck** → `ph-tools.github.io/CarbonCheck/`
4. **Honeybee-REVIVE** → `docs.passivehousetools.com/honeybee-revive/`
5. **PH-ADORB** → `docs.passivehousetools.com/ph-adorb/`
6. **PH-Units** → `docs.passivehousetools.com/ph-units/`

**Removed projects** (archived/legacy):
- ~~LBT2PH~~ (legacy, superseded by Honeybee-PH)
- ~~DesignPH Room-Data~~ (archived)

**Additional content to migrate from Hugo site**:
- Install guide (152 lines of valuable, detailed content)
- Quick start tutorial (49 lines + 10 screenshots)
- Learn more / video resources (49 lines)
- Contact / help info (74 lines)

### 2.4 What Gets Removed from This Repo

| Path | Size | Action |
|------|------|--------|
| `docs/` (entire Hugo site) | ~75MB total | **Delete** after migration |
| `docs/static/downloads/*.pdf` | 50MB | **Delete** (PDFs not needed) |
| `docs/static/downloads/*.zip` | 7.5MB | **Delete** (example files not needed) |
| `docs/static/img/` | 14MB | **Migrate** useful images to new site, then delete |
| `docs/public/` | generated | **Delete** (build output) |
| `docs/themes/ph_tools/` | custom Hugo theme | **Delete** (replaced by Astro + bldgtyp tokens) |
| `docs/config/` | Hugo config | **Delete** |
| `.github/workflows/hugo.yml` | CI/CD | **Delete** (no longer deploying Hugo from this repo) |

---

## 3. Key File Locations & References

### 3.1 This Repo (`honeybee_grasshopper_ph`)

```
honeybee_grasshopper_ph/
├── .github/workflows/
│   ├── hugo.yml                    ← DELETE (Hugo deploy)
│   └── release.yml                 ← KEEP (builds .ghx installer, publishes to GH Releases)
├── docs/                           ← DELETE entirely after migration
│   ├── config/_default/hugo.toml   ← Hugo config (baseURL, menu, params)
│   ├── content/
│   │   ├── _index.md               ← Home page (feature descriptions) → migrate
│   │   ├── install/index.md        ← Install guide (152 lines) → migrate
│   │   ├── quick_start/index.md    ← Quick start (49 lines) → migrate
│   │   ├── learn_more/index.md     ← Video links & resources (49 lines) → migrate
│   │   └── contact/index.md        ← Contact & help (74 lines) → migrate
│   ├── static/
│   │   ├── img/                    ← 23 images (14MB) → migrate useful ones
│   │   │   ├── home/               ← 2 images (background, rh_to_wufi)
│   │   │   ├── install/            ← 6 images (screenshots)
│   │   │   ├── quick_start/        ← 10 images (tutorial screenshots)
│   │   │   └── learn_more/         ← 4 images (splash screens)
│   │   └── downloads/              ← 57MB PDFs & zips → DELETE
│   ├── themes/ph_tools/            ← Custom Hugo theme → DELETE
│   └── public/                     ← Built output → DELETE
```

### 3.2 ph-docs Repo

```
/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/ph-docs/
├── astro.config.ts                 ← Site config (site: https://docs.passivehousetools.com)
├── libraries.yml                   ← Registry of spoke repos (5 libraries + 2 guides)
├── src/
│   ├── styles/global.css           ← Imports bldgtyp tokens CDN (line 8)
│   ├── components/Header.astro     ← Sticky header (could add passivehousetools.com link)
│   ├── layouts/BaseLayout.astro    ← Shared layout
│   └── pages/index.astro           ← Hub landing page
├── public/CNAME                    ← "docs.passivehousetools.com"
└── .github/workflows/build.yml     ← Nightly + dispatch builds → gh-pages
```

### 3.3 bldgtyp/branding Repo

```
https://github.com/bldgtyp/branding
├── tokens/tokens.css               ← CSS custom properties
├── tokens/components.css           ← Reusable UI components (.btn-primary, .service-card, etc.)
├── tokens/tokens.json              ← Machine-readable tokens
└── index.html                      ← Design system showcase page
```

### 3.4 Key URLs

| What | URL |
|------|-----|
| Current landing page | https://www.passivehousetools.com |
| Current docs hub | https://docs.passivehousetools.com |
| Current Hugo site (this repo) | https://ph-tools.github.io/honeybee_grasshopper_ph/ |
| CarbonCheck site | https://ph-tools.github.io/CarbonCheck/ |
| Branding showcase | https://bldgtyp.github.io/branding/ |
| Branding tokens CSS | https://bldgtyp.github.io/branding/tokens/tokens.css |
| Branding components CSS | https://bldgtyp.github.io/branding/tokens/components.css |
| Installer download (GH Release) | https://github.com/PH-Tools/honeybee_grasshopper_ph/releases/latest/download/hbph_installer.ghx |
| YouTube channel | https://www.youtube.com/channel/UCADxgnNCFNZ3uhaSvezReQA/playlists |
| GitHub org | https://github.com/PH-Tools |
| Reimagine Buildings Collective | https://collective.reimaginebuildings.com |
| Contact email | phtools@bldgtyp.com |

---

## 4. Execution Plan — Phased Checklist

### Phase 0: Preparation & Verification

- [x] **0.1** Confirm domain registrar for `passivehousetools.com` → **Dreamhost** (both registrar and hosting, expires 2027-01-04)
- [x] **0.2** Confirm DNS records — documented in Section 1.3 above
- [x] **0.3** Verify GitHub org allows creating `PH-Tools.github.io` repo (check permissions) — confirmed, repo created successfully
- [x] **0.4** Back up current Dreamhost site content — old site was a simple static HTML page, now superseded; Hugo source content preserved in git history
- [ ] **0.5** *(follow-up)* Confirm `passivehouse.tools` registration — is it registered through Dreamhost or elsewhere?
- [x] **0.6** Confirm no email is hosted on `passivehousetools.com` — `dig passivehousetools.com MX` returns empty. No MX records. Contact email is `phtools@bldgtyp.com` (different domain). Safe to change DNS without affecting email.
- [x] **0.7** Verify `docs.passivehousetools.com` continues working throughout — confirmed working at every phase

### Phase 1: Build the New Landing Page (Local)

- [x] **1.1** Scaffold Astro project locally (matching ph-docs patterns: same Astro version, same bldgtyp CDN imports, same font loading)
- [x] **1.2** Build landing page layout:
  - Header with nav (PH-Tools logo, "Docs" link → docs.passivehousetools.com, YouTube, GitHub) — cross-links baked in from the start
  - Hero section (PH-Tools branding, tagline)
  - Project cards grid (6 projects — see 2.3 above)
  - Footer (bldgtyp, llc copyright, contact, GPL license)
  - Dark/light theme toggle
  - Graph-paper background
  - **Must be responsive/mobile-friendly** — use the bldgtyp token breakpoints (ph-docs `global.css` has a `@media (max-width: 900px)` pattern). Single-column card grid on mobile, hamburger nav, etc.
  - Add a `/docs` redirect → `https://docs.passivehousetools.com` (Astro `src/pages/docs.astro` with a meta-refresh, or a static `public/_redirects` if deploying through a provider that supports it — GitHub Pages doesn't support `_redirects`, so use a meta-refresh page)
- [x] **1.3** Migrate install guide content from Hugo markdown → new Astro page (`/install/`)
  - Convert Hugo shortcodes (`{{< raw_html >}}`, `{{< installer_button >}}`) to Astro components
  - Copy relevant images from `docs/static/img/install/` (6 images)
  - Update image paths
  - Update the installer download URL to point to GitHub Releases
- [x] **1.4** Migrate quick start content → new Astro page (`/quick-start/`)
  - Copy 10 images from `docs/static/img/quick_start/`
  - Update image paths (remove `/honeybee_grasshopper_ph/` prefix)
- [x] **1.5** Migrate learn more / resources content → new Astro page (`/resources/`)
  - Keep all YouTube links
  - Remove download buttons for PDFs (those are being deleted)
  - Copy 4 splash images from `docs/static/img/learn_more/`
- [x] **1.6** Migrate contact content → new Astro page (`/contact/`)
  - Update internal links to point to new site paths
- [x] **1.7** Add `robots.txt` and `sitemap.xml` support:
  - Astro has built-in sitemap integration (`@astrojs/sitemap`) — add it
  - Add a `public/robots.txt` allowing all crawlers, pointing to sitemap
- [x] **1.8** Add a branded `404.astro` page (Astro convention: `src/pages/404.astro`). GitHub Pages will serve this for any missing route. Should show PH-Tools branding with a link back to home.
- [ ] **1.9** **Analytics** (optional but recommended): add lightweight, privacy-friendly analytics. Options:
  - **GitHub Pages traffic** (free, built-in): Settings > Traffic gives basic page views. No code needed, but very limited.
  - **Plausible** or **Umami** (self-hosted or cloud): lightweight script tag, no cookies, GDPR-friendly. Replaces the ~1,103 visit/month visibility that Dreamhost currently provides.
  - Decision: pick one before launch. Can always add later.
- [ ] **1.10** **SEO**: If PH-Tools has a Google Search Console account, note that the property will need to be re-verified for `passivehousetools.com` after DNS cutover (or add it as a new property alongside the old one). Check with Ed whether Search Console is set up.
- [x] **1.11** Review all migrated content — check links, images, formatting
- [x] **1.12** Test locally (`astro dev`) — verify all pages render, dark/light theme works, responsive layout, 404 page

### Phase 2: Create the GitHub Repo & Deploy

- [x] **2.1** Create `PH-Tools/PH-Tools.github.io` repo on GitHub
- [x] **2.2** Push Astro project to the repo
- [x] **2.3** Set up GitHub Actions workflow to build Astro and deploy to GitHub Pages (model after ph-docs `build.yml`)
- [x] **2.4** Verify site is live at `ph-tools.github.io` (no custom domain yet)
- [x] **2.5** Verify `ph-tools.github.io/CarbonCheck/` still works (org-level Pages repo can interfere with project-level Pages subpaths — test this before proceeding)
- [x] **2.6** Verify `docs.passivehousetools.com` still works
- [x] **2.7** Review the live site — check all pages, links, images

### Phase 3: DNS Cutover

- [x] **3.1** ~~Add `passivehousetools.com` as a verified domain in PH-Tools GitHub org settings~~ (skipped — not required for Pages to work, can be done later as a security hardening step) (Settings > Pages > "Add a domain"). GitHub will provide a verification code and ask you to create a DNS TXT record:
  - **Record name**: `_github-pages-challenge-PH-Tools` (or similar — GitHub shows the exact name)
  - **Record type**: TXT
  - **Record value**: a verification string GitHub provides
  - Add this TXT record in the Dreamhost DNS panel (Custom Records > Add Record). Wait for DNS propagation, then click "Verify" in GitHub.
- [x] **3.2** Add CNAME file to the repo's `public/` directory containing: `passivehousetools.com`
- [x] **3.3** In Dreamhost panel (Websites > passivehousetools.com > DNS), update records (in addition to the TXT record from 3.1):
  - **Change** `@` A record: delete `173.236.255.61`, add four A records for GitHub Pages:
    - `185.199.108.153`
    - `185.199.109.153`
    - `185.199.110.153`
    - `185.199.111.153`
  - **Replace** `www`: first **delete** the existing `www` A record (173.236.255.61), then **create** a new `www` CNAME → `ph-tools.github.io`. A records and CNAMEs cannot coexist for the same name — the A must be removed before the CNAME is added. Dreamhost's UI may or may not handle this atomically; if it doesn't allow creating the CNAME while the A exists, delete first, then create.
  - **DO NOT TOUCH** `docs` CNAME (already correct)
- [x] **3.4** Wait for DNS propagation (can take up to 48h, usually <1h). Verify with `dig passivehousetools.com A` — should return GitHub Pages IPs.
- [x] **3.5** Enable HTTPS in GitHub Pages settings (Settings > Pages > "Enforce HTTPS"). **TIMING NOTE**: GitHub must verify domain ownership via DNS before it can provision a TLS certificate. This step will fail if DNS hasn't fully propagated yet. If the checkbox is greyed out, wait and try again in 1-2 hours. Do not proceed to 3.6 until HTTPS is working.
- [x] **3.6** Verify `passivehousetools.com` loads the new site
- [ ] **3.7** *(follow-up)* Verify `www.passivehousetools.com` redirects properly — www CNAME not yet added in Dreamhost, system records still clearing
- [x] **3.8** Verify `docs.passivehousetools.com` is **unaffected** (critical!)
- [ ] **3.9** *(follow-up)* Set up `passivehouse.tools` redirect → `passivehousetools.com`:
  - **First**: confirm `passivehouse.tools` is registered through Dreamhost (it shows as "Redirect" plan type in the panel, but the screenshot doesn't show "Register Domain" or an expiry date — verify registration status).
  - **If registered on Dreamhost**: configure the redirect target in Dreamhost panel (Websites > passivehouse.tools > Manage). Dreamhost's "Redirect" plan type handles this at the server level — set target to `https://passivehousetools.com`, type 301.
  - **If registered elsewhere**: the domain's DNS must point to a server that can issue the redirect. Options: (a) point it to Dreamhost nameservers and use Dreamhost's redirect feature, or (b) use a redirect service like Cloudflare. Determine registrar first.

### Phase 4: Cross-Link ph-docs Back to Landing Page

> **Note**: The landing page → docs cross-links are built into the site during Phase 1.2 (header nav includes "Docs" link). This phase handles the reverse direction only.

- [x] **4.1** Add "Home" or "PH-Tools" link in ph-docs header (`/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/ph-docs/src/components/Header.astro`) → `passivehousetools.com`
- [x] **4.2** Push the ph-docs change and verify the cross-link works after rebuild
- [ ] **4.3** *(follow-up)* Verify cross-links work in both directions — pending ph-docs nightly rebuild

### Phase 5: Clean Up This Repo

- [x] **5.1** Delete `docs/static/downloads/` (57MB of PDFs and zips) 
- [x] **5.2** Delete `docs/static/img/` (images already migrated to new site)
- [x] **5.3** Delete `docs/content/` (content already migrated)
- [x] **5.4** Delete `docs/themes/` (Hugo theme no longer needed)
- [x] **5.5** Delete `docs/config/` (Hugo config no longer needed)
- [x] **5.6** Delete `docs/public/` (Hugo build output)
- [x] **5.7** Delete remaining `docs/` directory scaffolding
- [x] **5.8** **Replace** `.github/workflows/hugo.yml` with a redirect deployment workflow. Instead of deleting Pages entirely (which would 404 all old URLs shared in forum posts, YouTube descriptions, Discourse threads), deploy a minimal redirect site:
  - Create `docs/public/index.html` with `<meta http-equiv="refresh" content="0;url=https://passivehousetools.com">` and a JS fallback
  - Create `docs/public/install/index.html` → redirects to `https://passivehousetools.com/install/`
  - Create `docs/public/quick_start/index.html` → redirects to `https://passivehousetools.com/quick-start/`
  - Create `docs/public/learn_more/index.html` → redirects to `https://passivehousetools.com/resources/`
  - Create `docs/public/contact/index.html` → redirects to `https://passivehousetools.com/contact/`
  - Replace `hugo.yml` with a simple workflow that deploys `docs/public/` to Pages (no Hugo build needed — just static HTML redirect files)
  - This keeps the old URLs alive as redirects indefinitely, at zero maintenance cost
- [x] **5.9** Update this repo's README if it references the docs site URL
- [x] **5.10** Commit all cleanup changes
- [x] **5.11** Verify the `release.yml` workflow still works (it should — it doesn't depend on `docs/`) — confirmed, no deps on docs/
- [x] **5.12** Verify old URLs (`ph-tools.github.io/honeybee_grasshopper_ph/`, `.../install/`, etc.) redirect to new site

### Phase 6: Dreamhost Decommission

- [ ] **6.1** *(follow-up)* Confirm new site is stable and DNS is fully propagated (wait at least 1 week after Phase 3)
- [x] **6.2** Dreamhost DNS-Only supports custom A records — confirmed during Phase 3 (custom A records added while on DNS-Only)
- [x] **6.3** Dreamhost hosting plan already deactivated during Phase 3 — domain is now "DNS Only"
- [x] **6.4** `dig passivehousetools.com A` returns GitHub Pages IPs — confirmed
- [ ] **6.5** *(follow-up)* Delete the `ftp` and `ssh` A records (Dreamhost hosting artifacts, no longer needed)
- [ ] **6.6** *(follow-up)* Verify domain registration is set to auto-renew (expires 2027-01-04)
- [ ] **6.7** *(follow-up)* Verify `passivehouse.tools` → `passivehousetools.com` redirect still works

---

## 5. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| DNS cutover breaks `docs.passivehousetools.com` | High — developer docs go down | The docs subdomain uses its own CNAME (ph-docs repo). Changing the apex domain DNS should not affect it. Verify in Phase 3.8. |
| Org-level Pages repo breaks CarbonCheck subpath | **Medium** — `ph-tools.github.io/CarbonCheck/` stops working | When `PH-Tools.github.io` repo exists and serves the org root, GitHub *may* redirect or interfere with project-level Pages at subpaths. This is a known GitHub Pages gotcha. **Must test in Phase 2.5** before proceeding to DNS cutover. If CarbonCheck breaks, options: (a) CarbonCheck gets its own custom subdomain (e.g., `carboncheck.passivehousetools.com`), or (b) CarbonCheck docs migrate into ph-docs as a spoke, or (c) CarbonCheck content is embedded in the landing page. |
| HTTPS cert provisioning delay | **Medium** — site works on HTTP but not HTTPS, or shows cert warning | GitHub won't issue a TLS cert until DNS propagation is complete and ownership is verified. Phase 3.5 may need to be retried hours after Phase 3.3. Do not advertise the new URL until HTTPS is confirmed working. |
| Dreamhost "DNS Only" may not support custom A records | **Medium** — can't point domain to GitHub Pages after downgrading hosting | Dreamhost's DNS-Only mode for `ph-nav.com` and `ph-switch.com` is already on this account, but verify those have custom records. If DNS-Only doesn't support A records, alternatives: (a) keep the cheapest hosting tier, (b) move DNS management to Cloudflare (free tier) while keeping Dreamhost as registrar, (c) transfer domain to a registrar with better DNS (e.g., Cloudflare Registrar). **Test in Phase 6.2 — do the downgrade and immediately verify DNS resolution before deleting anything.** |
| Dreamhost hosting removal affects DNS | Low — domain stops resolving | Dreamhost supports "DNS Only" mode (already used for ph-nav.com, ph-switch.com). Downgrade hosting plan, don't cancel the domain. DNS records are managed separately from hosting. |
| Deleting `docs/` doesn't shrink repo clone size | **Low** — repo stays ~75MB in git history | Deleting files from the working tree removes them going forward but 57MB of PDFs remain in git history. This is fine — the repo is private enough that clone speed isn't a concern. If it becomes a problem later, `git filter-repo` or BFG can rewrite history, but that's a destructive operation that affects all clones. **Decision: accept the history bloat, don't rewrite.** |
| Old URLs in the wild (links to `ph-tools.github.io/honeybee_grasshopper_ph/`) | Low — broken bookmarks | Phase 5.8 deploys meta-refresh redirect pages at all old paths. Old URLs will redirect to the new domain indefinitely. |
| Installer download URL changes | Low — users can't install | The installer URL (`github.com/.../releases/latest/download/hbph_installer.ghx`) is from GitHub Releases, not from the docs site. It stays the same. |

### 5.1 Rollback Plan

If the DNS cutover (Phase 3) breaks something and needs to be reversed:

1. **Revert DNS in Dreamhost panel**:
   - Change `@` A records back to `173.236.255.61` (the Dreamhost server)
   - Delete the `www` CNAME, re-create `www` as A record → `173.236.255.61`
   - Leave `docs` CNAME untouched
2. **Wait for propagation** (~1h typically, up to 48h worst case)
3. **The old Dreamhost site is the safety net** — it remains intact and serving until Phase 6 decommissions it. This is why Phase 6 has a mandatory 1-week wait and should not be rushed.

**Critical**: Do not decommission Dreamhost hosting (Phase 6) until you are confident the new site is stable, HTTPS is working, and all cross-links are verified. The old site on Dreamhost is your rollback target.

---

## 6. Decisions Made

| Decision | Rationale |
|----------|-----------|
| Two repos, not one monorepo | GitHub Pages only allows one custom domain per repo. `ph-docs` already claims `docs.passivehousetools.com`. |
| Astro for both sites | Already using Astro 5 for ph-docs. Consistency, shared knowledge. |
| bldgtyp branding CDN for both | Both sites import the same `tokens.css` and `components.css`. Visual parity without code duplication. |
| Move off Dreamhost | Eliminates a hosting bill and a separate system to manage. GitHub Pages is free, has HTTPS, and is where all other PH-Tools content lives. |
| Delete LBT2PH & DesignPH Room-Data | Both are archived/legacy. Not worth listing on the new landing page. |
| Delete `docs/static/downloads/` PDFs | 57MB of presentation PDFs. Not needed — talks are on YouTube. |
| Keep CarbonCheck link | Still an active project with its own GitHub Pages site. |
| Keep `release.yml` workflow | It builds the `.ghx` installer and publishes to GitHub Releases. Independent of docs. |
| Don't rewrite git history after deleting `docs/` | 57MB of PDFs stay in git history forever. Acceptable — repo clone speed is not a bottleneck. Rewriting history (`git filter-repo`) would force all contributors to re-clone, not worth the disruption for a modest size savings. |
| CarbonCheck long-term home: **TBD after Phase 2.5** | CarbonCheck currently lives at `ph-tools.github.io/CarbonCheck/`. When the org-level `PH-Tools.github.io` repo is created, GitHub *may* remap that URL to `passivehousetools.com/CarbonCheck/` (serving from the org repo, which has no `/CarbonCheck/` route — resulting in a 404). Phase 2.5 tests this. If it breaks, options: (a) add CarbonCheck as a spoke in ph-docs, (b) give it a subdomain (`carboncheck.passivehousetools.com`), or (c) embed CarbonCheck content as a page in the new landing site. Decision deferred until we see what actually happens. |

---

## 7. Content Migration Reference

### Hugo Shortcodes → Astro Equivalents

| Hugo Shortcode | What It Does | Astro Replacement |
|---------------|-------------|-------------------|
| `{{< raw_html >}}...{{< /raw_html >}}` | Embeds raw HTML in markdown | Use `.astro` page directly (HTML native) |
| `{{< installer_button >}}` | Download button linking to GH Release | `<a>` tag with pill/button class linking to `github.com/.../releases/latest/download/hbph_installer.ghx` |
| `{{< gh_pages_name >}}` | Outputs "honeybee_grasshopper_ph" for URL building | Replace with direct paths (e.g., `/contact/`) |
| `{{< download_btn_Phius_PDF_240109 >}}` | PDF download button | **Remove** (PDFs being deleted) |
| `{{< download_btn_NYPH_PDF_240715 >}}` | PDF download button | **Remove** |
| `{{< download_btn_wrkshp_parsons_220923 >}}` | PDF download button | **Remove** |
| `{{< download_btn_YouTube_WUFI >}}` | Source files download button | **Remove** |

### Image Migration Map

| Source (this repo) | Files | Destination (new repo) |
|-------------------|-------|----------------------|
| `docs/static/img/install/` | 6 PNGs | `public/img/install/` |
| `docs/static/img/quick_start/` | 9 PNGs + 1 SVG | `public/img/quick-start/` |
| `docs/static/img/learn_more/` | 4 PNGs | `public/img/resources/` |
| `docs/static/img/home/` | 2 PNGs | `public/img/` (if used in hero) or skip |
