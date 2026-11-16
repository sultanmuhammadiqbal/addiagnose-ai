export const FIELDS = ["campaign", "spend", "impressions", "clicks", "conversions"];

const ALIASES = {
  campaign: ["campaign", "campaign name", "campaign names", "nama kampanye", "kampanye", "ad set name"],
  spend: ["amount spent", "amount spent usd", "amount spent idr", "cost", "spend", "biaya", "jumlah dibelanjakan", "biaya iklan"],
  impressions: ["impressions", "impression", "tayangan", "impr", "imps"],
  clicks: ["link clicks", "clicks", "klik tautan", "click", "klik", "outbound clicks"],
  conversions: ["conversions", "conversion", "results", "result", "hasil", "konversi", "purchases", "pembelian", "leads"]
};
const normalize = (value) => String(value ?? "").toLowerCase().replace(/[^a-z0-9 ]/g, " ").replace(/\s+/g, " ").trim();

export function guessMapping(headers) {
  const normalized = headers.map(normalize);
  const selected = {};
  for (const field of FIELDS) {
    const aliases = ALIASES[field];
    let idx = normalized.findIndex((name) => aliases.includes(name));
    if (idx < 0) {
      idx = normalized.findIndex((name) => aliases.some((alias) =>
        name.startsWith(alias + " ") && !(field === "spend" && /per|conversion|click|impression|ctr|cpc|cpa/.test(name))
      ));
    }
    selected[field] = idx >= 0 ? headers[idx] : "";
  }
  return selected;
}

// Input remains in its source currency. This is normalization, NEVER FX conversion.
export function numeric(value) {
  if (typeof value === "number") return Number.isFinite(value) ? value : NaN;
  let text = String(value ?? "").trim().replace(/[^0-9.,+\-]/g, "");
  if (!text) return NaN;
  const dot = text.lastIndexOf(".");
  const comma = text.lastIndexOf(",");
  if (dot >= 0 && comma >= 0) {
    const decimal = dot > comma ? "." : ",";
    const group = decimal === "." ? "," : ".";
    text = text.replaceAll(group, "").replace(decimal, ".");
  } else if (dot >= 0 || comma >= 0) {
    const sep = dot >= 0 ? "." : ",";
    const segments = text.split(sep);
    if (segments.length > 2 || (segments.length === 2 && segments[1].length === 3 && segments[0] !== "0")) {
      text = segments.join("");
    } else if (sep === ",") {
      text = text.replace(",", ".");
    }
  }
  const valueNumber = Number(text);
  return Number.isFinite(valueNumber) ? valueNumber : NaN;
}

function count(value) {
  const n = numeric(value);
  return Number.isFinite(n) && n >= 0 ? Math.round(n) : NaN;
}
function ratio(num, den, multiplier = 1) {
  return den > 0 ? (num / den) * multiplier : 0;
}
export function calculateTotals(rows) {
  const totals = rows.reduce((sum, row) => ({
    spend: sum.spend + row.spend,
    impressions: sum.impressions + row.impressions,
    clicks: sum.clicks + row.clicks,
    conversions: sum.conversions + row.conversions
  }), { spend: 0, impressions: 0, clicks: 0, conversions: 0 });
  return {
    ...totals,
    ctr: ratio(totals.clicks, totals.impressions, 100),
    cvr: ratio(totals.conversions, totals.clicks, 100),
    cpc: ratio(totals.spend, totals.clicks),
    cpa: ratio(totals.spend, totals.conversions)
  };
}
export function standardizeRows(rows, mapping) {
  for (const field of ["spend", "impressions", "clicks", "conversions"]) {
    if (!mapping[field]) throw new Error("Pilih kolom " + field + " sebelum menganalisis.");
  }
  const output = [];
  const invalid = [];
  rows.forEach((row, idx) => {
    const spend = numeric(row[mapping.spend]);
    const impressions = count(row[mapping.impressions]);
    const clicks = count(row[mapping.clicks]);
    const conversions = count(row[mapping.conversions]);
    if ([spend, impressions, clicks, conversions].some((x) => !Number.isFinite(x) || x < 0)) {
      invalid.push(idx + 1);
      return;
    }
    const campaign = String(mapping.campaign ? row[mapping.campaign] : "" || "").trim() || "Kampanye " + (idx + 1);
    output.push({
      campaign, spend, impressions, clicks, conversions,
      ctr: ratio(clicks, impressions, 100),
      cvr: ratio(conversions, clicks, 100),
      cpc: ratio(spend, clicks),
      cpa: ratio(spend, conversions)
    });
  });
  if (!output.length) throw new Error("Tidak ada baris valid. Periksa pemetaan dan format angka.");
  return { rows: output, totals: calculateTotals(output), invalidRows: invalid };
}
