import Papa from "papaparse";
import { guessMapping } from "./metrics.js";
const MAX_FILE_BYTES = 2 * 1024 * 1024;
const MAX_ROWS = 10000;

export async function readCsvFile(file) {
  if (file.size > MAX_FILE_BYTES) throw new Error("File maksimal 2 MB.");
  const bytes = new Uint8Array(await file.arrayBuffer());
  let charset = "utf-8";
  if ((bytes[0] === 0xff && bytes[1] === 0xfe) || (bytes.length > 8 && bytes[1] === 0 && bytes[3] === 0)) charset = "utf-16le";
  if (bytes[0] === 0xfe && bytes[1] === 0xff) charset = "utf-16be";
  return parseCsvText(new TextDecoder(charset, { fatal: false }).decode(bytes));
}
export function parseCsvText(text) {
  const content = String(text).replace(/^\uFEFF/, "");
  const parsed = Papa.parse(content, { header: false, skipEmptyLines: "greedy" });
  const lines = parsed.data.filter((line) => Array.isArray(line) && line.some((v) => String(v).trim()));
  if (!lines.length) throw new Error("File CSV kosong.");
  const keywords = /campaign|kampanye|cost|spend|biaya|impression|tayangan|click|klik|conversions|results|hasil|konversi/i;
  let headerIndex = -1;
  for (let i = 0; i < Math.min(lines.length, 30); i++) {
    const found = lines[i].filter((v) => keywords.test(String(v))).length;
    if (found >= 2) { headerIndex = i; break; }
  }
  if (headerIndex < 0) throw new Error("Header kampanye/iklan tidak ditemukan dalam 30 baris pertama.");
  const headers = lines[headerIndex].map((h) => String(h).trim());
  if (new Set(headers).size !== headers.length) throw new Error("Nama kolom duplikat; perbaiki header CSV.");
  const rows = lines.slice(headerIndex + 1, headerIndex + 1 + MAX_ROWS).map((cells) =>
    Object.fromEntries(headers.map((key, i) => [key, String(cells[i] ?? "").trim()]))
  );
  if (!rows.length) throw new Error("CSV tidak memiliki baris data.");
  return {
    headers, rows, mapping: guessMapping(headers),
    skippedLines: headerIndex, truncated: lines.length - headerIndex - 1 > MAX_ROWS,
    parseWarnings: parsed.errors.length
  };
}
