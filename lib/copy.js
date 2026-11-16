const cta = ["beli", "daftar", "hubungi", "promo", "klik", "pesan", "kunjungi", "pelajari", "dapatkan", "order", "subscribe", "buy", "sign up", "contact"];
const urgency = ["sekarang", "terbatas", "hari ini", "sebelum", "kehabisan", "limited", "today", "hurry", "now"];

function matching(text, words) {
  const lower = text.toLowerCase();
  return words.filter((word) => new RegExp("(^|[^\\p{L}])" + word.replace(/[.*+?^$\x7B\x7D()|[\]\\]/g, "\\$&") + "(?=$|[^\\p{L}])", "u").test(lower));
}

export function analyzeCopy(text) {
  const input = String(text ?? "").trim();
  if (!input) return null;
  const words = input.split(/\s+/).filter(Boolean).length;
  const first = input.split(/[.!\n]/)[0] || "";
  const hook = first.includes("?") || /apakah|bagaimana|bosan|inginkan|rahasia|kenapa|siapa|why|how/i.test(first);
  const foundCta = matching(input, cta);
  const foundUrgency = matching(input, urgency);
  const emojis = (input.match(/\p{Extended_Pictographic}/gu) || []).length;
  const recommendations = [];
  let score = 35;
  if (words >= 20 && words <= 80) score += 15;
  else recommendations.push(words < 20 ? "Tambah konteks dan manfaat produk." : "Ringkas pesan agar mudah dipindai.");
  if (hook) score += 15; else recommendations.push("Awali dengan hook yang relevan dengan kebutuhan audiens.");
  if (foundCta.length) score += 15; else recommendations.push("Sertakan CTA yang spesifik.");
  if (foundUrgency.length) score += 10; else recommendations.push("Tambahkan alasan bertindak sekarang hanya bila klaimnya benar.");
  if (emojis >= 2) score += 10;
  else if (emojis === 1) score += 5;
  else recommendations.push("Emoji opsional; gunakan hanya bila sesuai identitas brand.");
  return { score, words, characters: input.length, emojis, hook, foundCta, foundUrgency, recommendations };
}
