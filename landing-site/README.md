# Noetfield Runway Landing Site (Standalone)

This folder is a complete standalone marketing page for Noetfield Runway with:

- execution-focused positioning
- simulated live proof stream
- structured receipt output block
- responsive premium UI
- Cloudflare Pages deploy script

## Files

- `index.html` — page structure and commerce positioning sections
- `styles.css` — complete visual system, responsive layout, animations
- `app.js` — proof stream simulation and optional live endpoint mode
- `wrangler.toml` — Pages project configuration
- `deploy.sh` — repeatable deploy entrypoint

## Publish to Cloudflare Pages

```sh
cd /Users/sinakazemnezhad/Desktop/Noetfield-Systems/sina-governance-SSOT/landing-site
./deploy.sh
```

OAuth mode (recommended for local workstation):

```sh
env -u CLOUDFLARE_API_TOKEN -u CF_API_TOKEN wrangler login
cd /Users/sinakazemnezhad/Desktop/Noetfield-Systems/sina-governance-SSOT/landing-site
export CLOUDFLARE_PAGES_AUTH_MODE=oauth
./deploy.sh
```

Token mode (for automation/manual token auth):

```sh
cd /Users/sinakazemnezhad/Desktop/Noetfield-Systems/sina-governance-SSOT/landing-site
export CLOUDFLARE_PAGES_AUTH_MODE=token
# Paste the raw token only (no angle brackets, no quotes, no Bearer prefix)
export CLOUDFLARE_API_TOKEN=<raw_token>
./deploy.sh
```

Notes:

- `CLOUDFLARE_PAGES_AUTH_MODE=oauth` is now the default and prevents inherited API-token env variables from hijacking login.
- `CLOUDFLARE_ACCOUNT_ID` is not needed for `wrangler pages deploy` in this CLI version (4.103).
- Project name default is `noetfield-runway-standalone`.

## Optional env overrides

- `CLOUDFLARE_PAGES_PROJECT_NAME` (default: `noetfield-runway-standalone`)
- `CLOUDFLARE_PAGES_AUTH_MODE` (`oauth` default, `token` explicit)
- `CLOUDFLARE_API_TOKEN` (required only when `CLOUDFLARE_PAGES_AUTH_MODE=token`)
- `CLOUDFLARE_ENV` (default: `production`)
- `CLOUDFLARE_PAGES_BRANCH` (default: `main`)
- `CLOUDFLARE_PAGES_CUSTOM_DOMAIN` (informational notice in logs)

## Connect proof log to real live telemetry

`index.html` uses a local deterministic simulation by default for standalone deployment.
To wire live stream data:

1. Set `data-endpoint` on the run button:

```html
<button
  id="runSimulation"
  data-endpoint="/api/runway/live-sample"
>
  Run sample runway
</button>
```

2. Return JSON in this shape:

```json
{
  "feed": [
    {
      "status": "pass",
      "step": "goal_contract",
      "text": "Goal contract validated and locked.",
      "elapsedMs": 520
    }
  ]
}
```

If the endpoint is unavailable, the page falls back to simulation automatically.

## External verifier endpoint

After each deploy, this project writes proof files at:

- `https://noetfield-runway-standalone.pages.dev/verifier.json`
- `https://noetfield-runway-standalone.pages.dev/verifier.txt`
- `https://noetfield-runway-standalone.pages.dev/verifier`

It contains:

- project name
- deployed branch
- environment
- git commit
- UTC deploy timestamp
- expected auth mode

Use these commands to confirm they are reachable:

```sh
curl -fsSL "https://noetfield-runway-standalone.pages.dev/verifier.json" | jq
curl -fsSL "https://noetfield-runway-standalone.pages.dev/verifier.txt"
curl -fsSL "https://noetfield-runway-standalone.pages.dev/verifier"
```

## Conversion endpoint checks

The lead capture form now posts to `/lead` and returns JSON with a generated `leadId`.

After successful lead submit, users are redirected to `/thank-you` with plan/usecase context so the funnel is complete without dead-ends.

`/thank-you` and form-confirmation route:

```sh
curl -sS https://noetfield-runway-standalone.pages.dev/thank-you
```

```sh
curl -i -X GET https://noetfield-runway-standalone.pages.dev/lead
curl -i -X POST https://noetfield-runway-standalone.pages.dev/lead \
  -H 'content-type: application/json' \
  -d '{"email":"buyer@acme.com","company":"Acme","usecase":"decision-support","goal":"Pilot launch"}'
```

## Reuse for other ventures

Use this folder as the canonical landing template for NOETFIELD, TRUSTFIELD.CA,
SourceA, and SourceB commercial messaging and launch surfaces.
