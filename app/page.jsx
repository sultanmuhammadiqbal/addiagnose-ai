"use client";

import { useMemo, useState } from "react";
import { AreaChart, Area, BarChart, Bar, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import { Activity, ArrowUpRight, BarChart3, BrainCircuit, CheckCircle2, CircleAlert, FileSpreadsheet, LockKeyhole, MousePointer2, Radar, Sparkles, Target, UploadCloud, Wallet, Zap } from "lucide-react";
import { readCsvFile, parseCsvText } from "../lib/csv.js";
import { standardizeRows, FIELDS } from "../lib/metrics.js";
import { analyzeCopy } from "../lib/copy.js";

const demo = `Campaign Name,Amount Spent (USD),Impressions,Link Clicks,Results
Prospecting - Lookalike 1-5% - ID,450.50,22500,675,45
Retargeting - Catalog Sales - Buyers,280.00,14000,560,56
Competitor Audience Hook - V2,320.25,18500,370,18
Brand Awareness - Carousel - June,150.00,35000,525,5
Promo Ramadhan - Special Offer,600.00,42000,1470,105`;

const initialCopy = "Bosan iklan tidak menghasilkan? Kenali potensi campaign lewat analisis yang jelas. Audit performa iklan sekarang dan temukan peluang optimasi! 🚀✨";
const labels = { campaign: "Nama kampanye", spend: "Spend", impressions: "Impressions", clicks: "Clicks", conversions: "Conversions" };
const formatNum = (value, digits = 0) => Number(value || 0).toLocaleString("id-ID", { maximumFractionDigits: digits, minimumFractionDigits: digits });
const formatPct = (value) => formatNum(value, 2) + "%";
const fx = (value, currency) => new Intl.NumberFormat(currency === "IDR" ? "id-ID" : "en-US", { style: "currency", currency, maximumFractionDigits: currency === "IDR" ? 0 : 2 }).format(value || 0);
function Metric({ icon: Icon, label, value, hint, index }) {
  return <div className="metric"><div className="metric-top"><span>{label}</span><Icon size={18}/></div><strong>{value}</strong><small>{hint}</small><div className={"accent accent-"+index}/></div>;
}
function EmptyState({ children }) { return <div className="empty"><FileSpreadsheet size={30}/><p>{children}</p></div>; }
export default function Page() {
  const [dataset,setDataset] = useState(null);
  const [mapping,setMapping] = useState({});
  const [fileName,setFileName] = useState("");
  const [csvError,setCsvError] = useState("");
  const [currency,setCurrency] = useState("USD");
  const [tab,setTab] = useState("overview");
  const [copy,setCopy] = useState(initialCopy);
  const [accessCode,setAccessCode] = useState("");
  const [audit,setAudit] = useState("");
  const [auditError,setAuditError] = useState("");
  const [loading,setLoading] = useState(false);
  const [activeNav,setActiveNav] = useState(false);
  const calculated = useMemo(() => {
    if (!dataset) return null;
    try { return { ...standardizeRows(dataset.rows, mapping), error: "" }; }
    catch (err) { return { error: err.message, rows: [], totals: null, invalidRows: [] }; }
  },[dataset,mapping]);
  const copyResult = useMemo(() => analyzeCopy(copy), [copy]);
  function applyDataset(next,name) {
    setDataset(next); setMapping(next.mapping); setFileName(name); setCsvError(""); setAudit("");
    setTab("overview");
  }
  async function onUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    try { applyDataset(await readCsvFile(file),file.name); }
    catch (err) { setCsvError(err.message); }
    event.target.value = "";
  }
  async function runAudit() {
    if (!calculated?.rows?.length) { setAuditError("Muat dataset terlebih dahulu."); return; }
    setLoading(true); setAudit(""); setAuditError("");
    try {
      const response = await fetch("/api/audit", { method: "POST", headers: { "Content-Type": "application/json", "x-app-access-code": accessCode },
        body: JSON.stringify({ copy, campaigns: calculated.rows.slice(0,30) }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Audit gagal.");
      setAudit(data.result);
    } catch (err) { setAuditError(err.message); }
    finally { setLoading(false); }
  }
  const totals = calculated?.totals;
  const chartRows = (calculated?.rows || []).slice(0,12).map((r)=>({ ...r, short: r.campaign.length > 20 ? r.campaign.slice(0,18)+"…" : r.campaign }));
  return <div className="shell">
    <aside className={"sidebar "+(activeNav?"expanded":"")}>
      <div className="brand"><div className="brand-symbol"><Radar size={21}/></div><div><b>AdDiagnose<span>.AI</span></b><small>CAMPAIGN INTELLIGENCE</small></div></div>
      <div className="nav-label">WORKSPACE</div>
      {[["overview","Overview",BarChart3],["copy","Copywriting Lab",BrainCircuit],["ai","AI Audit",Sparkles]].map(([key,label,Icon]) =>
        <button key={key} className={"nav "+(tab===key?"selected":"")} onClick={()=>{setTab(key);setActiveNav(false);}}><Icon size={18}/>{label}{tab===key&&<span className="nav-dot"/>}</button>)}
      <div className="nav-label nav-spacer">DATA SOURCE</div>
      <div className="side-status"><FileSpreadsheet size={19}/><div><b>{fileName || "Belum ada dataset"}</b><small>{dataset ? dataset.rows.length+" baris diimpor" : "CSV Google / Meta Ads"}</small></div></div>
      <label className="upload"><UploadCloud size={18}/> Upload CSV<input type="file" accept=".csv,.tsv,text/csv,text/tab-separated-values" onChange={onUpload}/></label>
      <button className="secondary side-demo" onClick={()=>applyDataset(parseCsvText(demo),"Meta Ads · Demo")}>Gunakan data contoh</button>
      <div className="sidebar-footer"><div className="secure"><LockKeyhole size={15}/> Data CSV diproses di browser</div><small>AdDiagnose.AI / v2.0</small></div>
    </aside>
    <main className="main">
      <header className="topbar"><button className="mobile-menu" onClick={()=>setActiveNav(!activeNav)}>☰</button><div className="breadcrumb">WORKSPACE <span>/</span> {tab === "overview" ? "OVERVIEW" : tab==="copy"?"COPYWRITING LAB":"AI AUDIT"}</div><div className="top-right"><span className="status-dot"/> SYSTEM READY <div className="avatar">AD</div></div></header>
      <div className="content">
        <div className="heading"><div><div className="eyebrow"><Activity size={15}/> INTELLIGENT AD PERFORMANCE</div><h1>{tab==="overview"?"Performance Overview":tab==="copy"?"Copywriting Lab":"AI Creative Audit"}</h1><p>{tab==="overview"?"Diagnosa performa kampanye berdasarkan data nyata, bukan tebakan.":tab==="copy"?"Periksa elemen persuasi copy sebelum kamu melakukan eksperimen.":"Hubungkan performa iklan dengan hipotesis optimasi berbantuan AI."}</p></div><div className="pill"><span className="status-dot"/> {dataset?"DATA LOADED":"AWAITING DATA"}</div></div>
        {csvError && <div className="alert"><CircleAlert size={17}/>{csvError}</div>}
        {dataset && <div className="data-banner"><div><CheckCircle2 size={18}/><strong>{fileName}</strong><span>{dataset.rows.length} baris • {dataset.skippedLines} baris metadata dilewati{dataset.truncated?" • dibatasi 10.000 baris":""}{dataset.parseWarnings?" • format CSV memiliki peringatan":""}</span></div><select aria-label="Mata uang sumber data" value={currency} onChange={e=>setCurrency(e.target.value)}><option value="USD">Sumber USD</option><option value="IDR">Sumber IDR</option><option value="EUR">Sumber EUR</option></select></div>}
        {tab==="overview" && <>
          {!dataset ? <div className="onboarding"><div className="orb"><Radar size={44}/></div><h2>Insight dimulai dari data</h2><p>Upload laporan CSV Google Ads atau Meta Ads. Perhitungan berjalan secara lokal di browser, tanpa mengirim file ke server.</p><label className="primary upload-big"><UploadCloud size={19}/> Upload Data CSV<input type="file" accept=".csv,.tsv" onChange={onUpload}/></label><button className="secondary" onClick={()=>applyDataset(parseCsvText(demo),"Meta Ads · Demo")}>Explore dengan data demo <ArrowUpRight size={16}/></button></div> : <>
          <section className="panel mapper"><div className="panel-head"><div><h3>Column Mapping</h3><p>Pastikan setiap metrik mengarah ke kolom yang benar.</p></div><span className="tag">SMART DETECTION</span></div><div className="mapping-grid">{FIELDS.map(field=><label key={field}>{labels[field]}<select value={mapping[field]||""} onChange={e=>setMapping({...mapping,[field]:e.target.value})}><option value="">— Tidak tersedia —</option>{dataset.headers.map(h=><option key={h} value={h}>{h}</option>)}</select></label>)}</div></section>
          {calculated?.error ? <div className="alert"><CircleAlert size={17}/>{calculated.error}</div> : <>
          {!!calculated.invalidRows.length && <div className="alert"><CircleAlert size={16}/>{calculated.invalidRows.length} baris dilewati karena angka kosong/tidak valid. Periksa format CSV dan pemetaan kolom.</div>}
          <div className="metrics-grid"><Metric index="1" icon={Wallet} label="TOTAL AD SPEND" value={fx(totals.spend,currency)} hint="Total biaya kampanye"/><Metric index="2" icon={MousePointer2} label="OVERALL CTR" value={formatPct(totals.ctr)} hint={formatNum(totals.clicks)+" / "+formatNum(totals.impressions)+" impressions"}/><Metric index="3" icon={Target} label="OVERALL CVR" value={formatPct(totals.cvr)} hint={formatNum(totals.conversions)+" konversi"}/><Metric index="4" icon={Zap} label="AVG. COST PER RESULT" value={fx(totals.cpa,currency)} hint="CPA = total spend / total conversions"/></div>
          <div className="charts-grid"><section className="panel"><div className="panel-head"><div><h3>Spend by Campaign</h3><p>Pengeluaran per kampanye</p></div><BarChart3 size={18}/></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartRows}><CartesianGrid stroke="#263144" strokeDasharray="3 5" vertical={false}/><XAxis dataKey="short" tick={{fill:"#8995a8",fontSize:10}} interval={0} angle={-20} textAnchor="end" height={60}/><YAxis tick={{fill:"#8995a8",fontSize:11}}/><Tooltip contentStyle={{background:"#172033",border:"1px solid #39465d",borderRadius:12}}/><Bar dataKey="spend" fill="#a18aff" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></div></section><section className="panel"><div className="panel-head"><div><h3>Engagement vs Conversion</h3><p>CTR dan CVR (%) per kampanye</p></div><Activity size={18}/></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartRows}><CartesianGrid stroke="#263144" strokeDasharray="3 5" vertical={false}/><XAxis dataKey="short" tick={{fill:"#8995a8",fontSize:10}} interval={0} angle={-20} textAnchor="end" height={60}/><YAxis tick={{fill:"#8995a8",fontSize:11}}/><Tooltip contentStyle={{background:"#172033",border:"1px solid #39465d",borderRadius:12}}/><Legend/><Bar dataKey="ctr" name="CTR %" fill="#37d6be" radius={[5,5,0,0]}/><Bar dataKey="cvr" name="CVR %" fill="#f4a56e" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></div></section></div>
          <section className="panel table-panel"><div className="panel-head"><div><h3>Campaign Breakdown</h3><p>Semua angka rasio dihitung ulang dari metrik dasar. Preview maksimal 500 baris.</p></div><span className="tag">{calculated.rows.length} CAMPAIGNS</span></div><div className="table-wrap"><table><thead><tr>{["Campaign","Spend","Impr.","Clicks","Conv.","CTR","CVR","CPC","CPA"].map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{calculated.rows.slice(0,500).map((r,i)=><tr key={i}><td title={r.campaign}>{r.campaign}</td><td>{fx(r.spend,currency)}</td><td>{formatNum(r.impressions)}</td><td>{formatNum(r.clicks)}</td><td>{formatNum(r.conversions)}</td><td>{formatPct(r.ctr)}</td><td>{formatPct(r.cvr)}</td><td>{fx(r.cpc,currency)}</td><td>{fx(r.cpa,currency)}</td></tr>)}</tbody></table></div></section>
          </>}</>}
        </>}
        {tab==="copy" && <div className="lab-grid"><section className="panel"><div className="panel-head"><div><h3>Copywriting Input</h3><p>Tempel copywriting iklan untuk analisis heuristik.</p></div><BrainCircuit size={18}/></div><textarea value={copy} onChange={e=>setCopy(e.target.value)} maxLength={4000} rows={12} placeholder="Tulis copywriting di sini..."/><div className="text-foot">{copy.length}/4000 karakter</div></section><section className="panel"><div className="panel-head"><div><h3>Creative Health Score</h3><p>Indikator heuristik, bukan prediksi hasil iklan.</p></div><Sparkles size={18}/></div>{copyResult?<><div className="score"><div><strong>{copyResult.score}</strong><span>/100</span></div><p>{copyResult.words} kata • {copyResult.emojis} emoji</p></div><div className="checks">{[["Hook pembuka",copyResult.hook],["Call to action",copyResult.foundCta.length>0],["Elemen urgensi",copyResult.foundUrgency.length>0]].map(([name,ok])=><div key={name}><span>{name}</span><b className={ok?"good":"bad"}>{ok?"TERDETEKSI":"BELUM ADA"}</b></div>)}</div><h4>Rekomendasi</h4>{copyResult.recommendations.length?copyResult.recommendations.map((rec,i)=><p className="recommendation" key={i}>{rec}</p>):<p className="recommendation">Semua indikator heuristik terdeteksi. Tetap validasi dengan eksperimen nyata.</p>}</>:<EmptyState>Masukkan teks untuk dianalisis.</EmptyState>}</section></div>}
        {tab==="ai" && <div className="lab-grid"><section className="panel"><div className="panel-head"><div><h3>Audit Setup</h3><p>Butuh CSV, copywriting, dan kode akses aplikasi.</p></div><LockKeyhole size={18}/></div><label className="form-label">Kode akses aplikasi<input type="password" autoComplete="off" value={accessCode} onChange={e=>setAccessCode(e.target.value)} placeholder="APP_ACCESS_CODE"/></label><label className="form-label">Copywriting<textarea rows={7} maxLength={4000} value={copy} onChange={e=>setCopy(e.target.value)}/></label><p className="muted">Hanya data metrik (maks. 30 kampanye) dan copywriting yang dikirim ke Gemini saat kamu menekan tombol audit. Dataset lengkap tetap di browser.</p><button className="primary action" disabled={!totals||loading||!accessCode||!copy.trim()} onClick={runAudit}><Sparkles size={17}/>{loading?"Menganalisis...":"Jalankan AI Audit"}</button>{auditError&&<div className="alert">{auditError}</div>}</section><section className="panel"><div className="panel-head"><div><h3>AI Recommendations</h3><p>Temuan, hipotesis, dan rencana eksperimen.</p></div><BrainCircuit size={18}/></div>{audit?<div className="audit-result">{audit}</div>:<EmptyState>Hasil audit Gemini akan muncul di sini. Audit adalah hipotesis, bukan bukti kausal.</EmptyState>}</section></div>}
        <footer>AdDiagnose.AI <span>•</span> Data-driven decisions, human-verified insights <span>•</span> v2.0</footer>
      </div>
    </main>
  </div>;
}
