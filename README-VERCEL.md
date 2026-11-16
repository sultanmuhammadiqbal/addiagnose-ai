# AdDiagnose.AI v2 — Next.js + Vercel

The original Streamlit app (`app.py`) is preserved for reference; the Vercel app is in `app/`.

## Getting started

Requires Node.js 20.9 or newer.

```bash
npm install
npm test
npm run dev
```

Open http://localhost:3000.

## Vercel deploy

1. Import this GitHub repository into Vercel (use the migration branch for Preview).
2. Framework preset: Next.js. Root directory: repository root.
3. Add environment variables in project settings:
   - `GEMINI_API_KEY` — server-side Google Gemini API key.
   - `APP_ACCESS_CODE` — a long, private passphrase for people allowed to run AI audits.
   - `GEMINI_MODEL` — optional override, default `gemini-2.5-flash`. Verify model availability for your account.
4. Deploy. Do **not** prefix any secret with `NEXT_PUBLIC_`.
5. To run audits, enter APP_ACCESS_CODE in the AI Audit screen. CSV parsing and local copy scoring do not require this code.

## Data handling

CSV parsing, metric calculations and local copy scoring are done in the browser. AI audit sends only up to 30 normalized campaign records and user-provided copy to a server endpoint, which sends them to Gemini. Avoid uploading sensitive client data without permission. There is no database or analytics in this MVP.

## Metric rules

All ratios are re-calculated using raw counts: CTR = clicks / impressions, CVR = conversions / clicks, CPC = spend / clicks, CPA = spend / conversions. For zero denominators the display uses zero, not NaN. Currency selector only labels the source currency: there is no FX conversion. CSV values with ambiguous `1.234` or `1,234` separator conventions need review before use.

## Limitations before public multi-tenant launch

This is an access-code gated MVP, **not** user account authentication. In-memory throttling in Vercel functions is best-effort only and not distributed; add persistent IP/account rate limits, user authentication, billing protections, monitoring, and stronger security before marketing public access. Up to 2 MB / 10k CSV rows are allowed in the browser. Charts show first 12 campaigns, table first 500, Gemini first 30. All platform-specific metric definitions must be validated (e.g. Meta Link Clicks vs Google Clicks, campaign result attribution). Gemini analysis is hypothetical, not a causal proof.

## Original Python app

The existing Streamlit `app.py`, `requirements.txt`, and samples remain in the repo. Run them separately using `streamlit run app.py` if needed.
