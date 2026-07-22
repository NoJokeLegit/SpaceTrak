# Orbital data pipeline — setup

Goal: Space-Track (source) → GitHub (fetch + host) → jsDelivr (free CDN) → your app.
No server to run. Cost: $0.

## What each file does
- `fetch_snapshot.py` — logs into Space-Track once, pulls the on-orbit catalog,
  splits it into layers (`featured`, `payloads`, `starlink`, `debris`, `all`),
  and writes plain + gzipped JSON into a `public/` folder.
- `snapshot.yml` — GitHub Actions workflow. Runs the script every hour at :19 and
  commits the refreshed snapshot back to the repo.

## One-time setup (~15 min)

1. **Create a GitHub repo** (public is fine — the TLE data is public), e.g. `orbit-data`.

2. **Add the files:**
   - `fetch_snapshot.py` at the repo root.
   - `snapshot.yml` at `.github/workflows/snapshot.yml`.

3. **Add your Space-Track login as secrets**
   (repo → Settings → Secrets and variables → Actions → New repository secret):
   - `SPACETRACK_USER` = your Space-Track email
   - `SPACETRACK_PASS` = your Space-Track password
   (Secrets are encrypted; they never appear in the committed files or logs.)

4. **Run it once manually:** repo → Actions tab → "Fetch orbital snapshot" → Run workflow.
   After ~1 min you should see a new commit with files in `public/`.

## The CDN URLs your app calls

jsDelivr serves any file in a public GitHub repo, cached globally, free, no setup:

```
https://cdn.jsdelivr.net/gh/<user>/<repo>@main/public/featured.json.gz
https://cdn.jsdelivr.net/gh/<user>/<repo>@main/public/starlink.json.gz
https://cdn.jsdelivr.net/gh/<user>/<repo>@main/public/debris.json.gz
```

The app downloads the layer(s) it needs, unzips, and runs SGP4 locally to animate.

> Note: jsDelivr caches `@main` aggressively (~12h). For always-fresh data you can
> pin a purge or use a commit hash; for a cinematic app, ~12h old data looks identical,
> so `@main` is fine. If you later outgrow jsDelivr, point the app at Cloudflare R2
> (also free egress) — only the base URL changes.

## In the app
- Ship `featured.json.gz` bundled inside the app for instant first-launch play.
- On launch (or Background App Refresh), if the local copy is >1 day old, download a
  fresh one from the CDN.
- Feed the TLE lines to an SGP4 library (Swift: pull positions on-device at 60fps).

## Guardrails (don't get your account suspended)
- The workflow runs once/hour — do not lower the cron interval.
- One bulk query per run (already the case) — never loop per-satellite.
- Keep the off-peak `:19` minute.
