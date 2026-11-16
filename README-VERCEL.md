# AdDiagnose.AI v2 — Next.js + Vercel

Requires Node.js 20.9 or newer.

## Getting started

```bash
npm install
npm test
npm run dev
```

Open http://localhost:3000.

## Demo deployment (no API key needed)

Set `DEMO_MODE=true` in Vercel Project Settings. Leave `GEMINI_API_KEY` and `APP_ACCESS_CODE` unset. Redeploy after changing environment variables.

Demo mode returns a clearly labelled simulated audit based on the submitted campaign metrics. It does not call Gemini and is intended for UI walkthroughs and portfolio demonstrations, not as a substitute for AI analysis.

## Live Gemini deployment

1. Set `DEMO_MODE=false`.
2. Set `GEMINI_API_KEY` to a server-side Google AI Studio API key.
3. Set `APP_ACCESS_CODE` to a long, private access passphrase.
4. Optionally set `GEMINI_MODEL`; default is `gemini-2.5-flash`.
5. Redeploy. Never expose secrets with a `NEXT_PUBLIC_` prefix.

## Vercel setup

Import this repository, select branch `feat/nextjs-vercel-migration` for Preview, choose Next.js, and use repository root as Root Directory.

## Data handling

CSV parsing, metric calculations and local copy scoring happen in the browser. Only up to 30 normalized campaign records and copywriting are sent to the audit endpoint when the user explicitly starts an audit. Demo mode uses deterministic rule-based sample commentary; live mode sends this limited payload to Gemini. Avoid uploading sensitive client data without permission.

## Metric rules

CTR = clicks / impressions, CVR = conversions / clicks, CPC = spend / clicks, CPA = spend / conversions. Zero denominators display zero. Currency selector labels source currency; it does not convert FX. Ambiguous number formats such as `1.234` require manual review.

## Limitations before public launch

This MVP does not provide per-user accounts. `APP_ACCESS_CODE` is a shared passphrase; in-memory throttling is best-effort and not distributed. Add account authentication, persistent rate limits, usage budgets, monitoring, and security review before public multi-user exposure. Up to 2 MB / 10k CSV rows are accepted; charts show 12 campaigns, table 500, and live Gemini audit 30. Validate platform-specific metric definitions and attribution before operational use.

## Original Python app

The original Streamlit `app.py`, `requirements.txt`, and sample CSVs remain intact.
