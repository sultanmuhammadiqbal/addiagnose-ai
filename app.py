import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import io

# Set page configuration
st.set_page_config(
    page_title="AdDiagnose.AI - Premium Ad Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply font to elements */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Title styling */
    .title-text {
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #8A2387, #E94057, #F27121);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        margin-bottom: 0px;
    }
    
    .subtitle-text {
        font-size: 1.1rem;
        color: #718096;
        margin-bottom: 25px;
    }
    
    /* Premium visual cards styling */
    .kpi-card {
        background: linear-gradient(135deg, #1f2937, #111827);
        border: 1px solid #374151;
        padding: 24px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: #ec4899;
    }
    
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(to right, #f43f5e, #ec4899, #d946ef);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Box result AI styling */
    .ai-box {
        background-color: #1e1b4b;
        border: 1px solid #4f46e5;
        border-left: 6px solid #818cf8;
        padding: 25px;
        border-radius: 12px;
        margin-top: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: #e2e8f0;
    }
    
    .ai-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #c7d2fe;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .diagnose-card {
        background-color: #1e1e30;
        border-left: 6px solid #8A2387;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
    }
    
    .metric-table th {
        background-color: #2D3748 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session States
if "ai_audit_result" not in st.session_state:
    st.session_state.ai_audit_result = None
if "user_copy_text" not in st.session_state:
    st.session_state.user_copy_text = (
        "Beli Sekarang! Promo Diskon 50% hanya untuk hari ini.\n"
        "Apakah Anda bosan dengan dashboard iklan yang membingungkan?\n"
        "Jangan khawatir, gunakan AdDiagnose.AI. Hubungi kami sebelum kehabisan slot promo terbatas ini! 🔥🚀"
    )
if "demo_data_loaded" not in st.session_state:
    st.session_state.demo_data_loaded = False
if "df_standard" not in st.session_state:
    st.session_state.df_standard = None


# Helper Functions
def read_csv_robust(uploaded_file):
    """
    Reads an uploaded CSV or TSV file. Detects if it is a tab-separated Google Ads export
    with 2 lines of metadata, and parses it using sep='\t' and skiprows=2. Otherwise,
    parses using the general post-load header scanner.
    Returns:
        df (pd.DataFrame): Crop-standardized DataFrame with true column names
        skip_rows (int): Number of rows skipped to reach header
    """
    file_bytes = uploaded_file.getvalue()
    
    # 1. Detect UTF-16 encoding based on BOM or null bytes
    is_utf16 = False
    if file_bytes.startswith(b'\xff\xfe') or file_bytes.startswith(b'\xfe\xff'):
        is_utf16 = True
    else:
        try:
            sample_text = file_bytes[:1000].decode('latin-1')
            if sample_text.count('\x00') > 10:
                is_utf16 = True
        except Exception:
            pass
            
    # 2. Decode the raw bytes safely
    if is_utf16:
        try:
            raw_text = file_bytes.decode('utf-16', errors='ignore')
        except Exception:
            raw_text = file_bytes.decode('latin-1')
    else:
        try:
            raw_text = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            raw_text = file_bytes.decode('latin-1')
            
    clean_text = raw_text.replace('\x00', '')
    
    # 3. Detect if it is a TAB-separated file (typical Google Ads export)
    # Count tabs in the first few lines
    lines = clean_text.splitlines()
    first_few_lines = "\n".join(lines[:5])
    has_tabs = first_few_lines.count('\t') > 5
    
    if has_tabs:
        # Load directly using sep='\t', skiprows=2, on_bad_lines='skip'
        # Pass clean string via StringIO to bypass encoding issues
        df = pd.read_csv(
            io.StringIO(clean_text),
            sep='\t',
            skiprows=2,
            engine='python',
            on_bad_lines='skip'
        )
        # Clean column names
        df.columns = df.columns.astype(str).str.strip()
        skip_rows = 2
        return df, skip_rows
        
    # 4. Otherwise, use our general post-load header scanner for standard CSVs
    df_raw = pd.read_csv(
        io.StringIO(clean_text),
        header=None,
        sep=None,
        engine='python',
        on_bad_lines='skip'
    )
    
    header_keywords = ['campaign', 'spent', 'impression', 'click', 'cost', 'id', 'nama', 'performa', 'results', 'conversions', 'clicks', 'tayangan', 'biaya', 'klik']
    skip_rows = 0
    header_found = False
    
    for idx in range(min(len(df_raw), 20)): # Scan first 20 rows
        row_values = df_raw.iloc[idx].astype(str).str.lower().tolist()
        match_count = sum(1 for kw in header_keywords if any(kw in val for val in row_values))
        if match_count >= 2:
            # Set columns using original case-sensitive headers from this row
            df_raw.columns = df_raw.iloc[idx].tolist()
            # Crop the dataframe to take data rows after the header
            df_raw = df_raw.iloc[idx+1:].reset_index(drop=True)
            skip_rows = idx
            header_found = True
            break
            
    if not header_found:
        # Fallback if no header row was matched
        df_raw.columns = [f"Column {i+1}" for i in range(df_raw.shape[1])]
        skip_rows = 0
        
    # Clean column names
    df_raw.columns = df_raw.columns.astype(str).str.strip()
    return df_raw, skip_rows


def guess_default_column(raw_cols, keywords, exclude_keywords=None):
    """
    Scans list of columns and guesses default index based on keywords & exclusions.
    """
    for idx, col in enumerate(raw_cols):
        c_low = str(col).strip().lower()
        if any(kw in c_low for kw in keywords):
            if exclude_keywords and any(ex in c_low for ex in exclude_keywords):
                continue
            return idx
    return 0


def analyze_copywriting(text):
    """
    Diagnoses copy text using psychological rules and standard advertising cues.
    """
    if not text.strip():
        return None
        
    char_count = len(text)
    word_count = len(text.split())
    
    sentences = re.split(r'[.!?]+', text.strip())
    first_sentence = sentences[0] if sentences else ""
    has_hook = "?" in first_sentence or any(w in first_sentence.lower() for w in ["apakah", "bagaimana", "bosan", "inginkan", "rahasia", "kenapa", "siapa"])
    
    cta_words = ["beli", "daftar", "hubungi", "promo", "diskon", "klik", "order", "pesan", "kunjungi", "pelajari", "dapatkan", "join", "subscribe", "buy", "sign up", "contact"]
    found_ctas = [w for w in cta_words if re.search(r'\b' + w + r'\b', text.lower())]
    has_cta = len(found_ctas) > 0
    
    urgency_words = ["sekarang", "terbatas", "hari ini", "hanya", "cepat", "sebelum", "kehabisan", "jangan lewatkan", "now", "limited", "today", "only", "hurry"]
    found_urgency = [w for w in urgency_words if re.search(r'\b' + w + r'\b', text.lower())]
    has_urgency = len(found_urgency) > 0
    
    emojis = re.findall(r'[\u2600-\u27BF]|[\u1F300-\u1F64F]|[\u1F680-\u1F6FF]|[\u1F1E0-\u1F1FF]', text)
    emoji_count = len(emojis)
    
    score = 40
    recs = []
    
    if 20 <= word_count <= 80:
        score += 15
    else:
        if word_count < 20:
            recs.append("✍️ **Terlalu Singkat**: Tambahkan penjelasan manfaat produk Anda agar pembaca lebih tuntas memahami penawaran.")
        else:
            recs.append("✍️ **Terlalu Panjang**: Pertimbangkan untuk menyingkat teks agar audiens tidak lelah membaca di feed social media.")
            
    if has_hook:
        score += 15
    else:
        recs.append("🪝 **Tambahkan Hook**: Awali copywriting dengan kalimat tanya atau kata pemancing perhatian di kalimat pertama (contoh: *'Bosan dengan...?'* atau *'Rahasia sukses...'*).")
        
    if has_cta:
        score += 15
    else:
        recs.append("🎯 **Tambahkan CTA (Call-to-Action)**: Tuntun pembaca untuk bertindak dengan jelas (contoh: *'Daftar Sekarang'*, *'Klik Link Ini'*).")
        
    if has_urgency:
        score += 10
    else:
        recs.append("⏳ **Tambahkan Urgensi**: Beri kesan kelangkaan agar pembaca segera bertindak (contoh: *'Terbatas hanya hari ini'*, *'Sisa 5 slot lagi'*).")
        
    if emoji_count >= 2:
        score += 10
    elif emoji_count == 1:
        score += 5
        recs.append("🔥 **Tambahkan Emoji**: Gunakan 2-3 emoji yang relevan untuk memecah teks tebal dan menarik visual mata.")
    else:
        recs.append("🔥 **Gunakan Emoji**: Tambahkan beberapa emoji untuk mempercantik struktur teks copywriting Anda.")
        
    score = min(score, 100)
    
    if score >= 85:
        rating = "Sangat Kuat (Optimal) 🔥"
        rating_color = "#10B981"
    elif score >= 70:
        rating = "Kuat (Bagus) 👍"
        rating_color = "#3B82F6"
    elif score >= 50:
        rating = "Cukup (Perlu Optimasi) 📈"
        rating_color = "#F59E0B"
    else:
        rating = "Perlu Perbaikan Segera ⚠️"
        rating_color = "#EF4444"
        
    return {
        "score": score,
        "rating": rating,
        "rating_color": rating_color,
        "char_count": char_count,
        "word_count": word_count,
        "emoji_count": emoji_count,
        "has_hook": has_hook,
        "has_cta": has_cta,
        "has_urgency": has_urgency,
        "recommendations": recs,
        "found_ctas": found_ctas,
        "found_urgency": found_urgency
    }


def audit_ad_creative(api_key, df_metrics, copy_text):
    """
    Audits the copywriting based on local Pandas campaign performance metrics using Gemini.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        return "Error: Pustaka `google-generativeai` belum terinstal. Silakan instal terlebih dahulu."
        
    try:
        genai.configure(api_key=api_key)
        
        metrics_df_clean = df_metrics[['Campaign', 'Spend', 'Impressions', 'Clicks', 'Conversions', 'CTR (%)', 'CVR (%)']]
        metrics_str = metrics_df_clean.to_string(index=False)
        
        prompt = f"""
Berikut adalah data performa iklan saat ini (dari Pandas lokal):
```
{metrics_str}
```

Berikut adalah teks copywriting iklan yang sedang berjalan:
"{copy_text}"

Analisis keterkaitan antara salinan copywriting tersebut dengan data performa iklan di atas. Evaluasi secara kritis hubungan antara CTR (Click-Through Rate) dan CVR (Conversion Rate).

Berikan laporan audit dalam format Markdown yang rapi dengan memuat dua bagian utama berikut:
1. **Diagnosis Kerusakan**: Mengapa performa iklannya boncos atau kurang optimal berdasarkan data performa angka di atas. Hubungkan dengan kelemahan psikologis copy yang sedang berjalan.
2. **Solusi Taktis**: Berikan 3 rekomendasi perbaikan Hook baru (kalimat pembuka copywriting) yang menargetkan kelemahan psikologis dari teks lama agar relevan dengan target audiens dan mampu meningkatkan CTR & CVR.
"""

        system_instruction = (
            "Anda adalah pakar Media Buyer dan Psikologi Iklan Digital berskala internasional. "
            "Tugas Anda adalah mengaudit salinan iklan (copywriting) berdasarkan data metrik (CTR, CVR) "
            "yang bersumber dari data Pandas lokal."
        )

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"🚨 Gagal memproses permintaan ke Gemini API. Pastikan API Key Anda valid.\n\nDetail Error: {str(e)}"


# Main Layout Header
col_header_left, col_header_right = st.columns([4, 1])
with col_header_left:
    st.markdown('<h1 class="title-text">AdDiagnose.AI 🎯</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Platform Diagnostik Kinerja Iklan dan Psikologi Copywriting lokal & AI Anda</p>', unsafe_allow_html=True)
with col_header_right:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("`Versi MVP 1.7 (Manual Mapper)`", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/nolan/96/bullseye.png", width=70)
st.sidebar.header("Konfigurasi Data")

# Currency setting for formatting
currency_choice = st.sidebar.selectbox(
    "Mata Uang Dashboard",
    ["IDR (Rp)", "USD ($)", "EUR (€)"],
    index=0
)
currency_symbol = "Rp " if "IDR" in currency_choice else ("$ " if "USD" in currency_choice else "€ ")

# Gemini API Integration Section in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Integrasi Gemini AI")
gemini_api_key = st.sidebar.text_input(
    "Masukkan Gemini API Key Anda:",
    type="password",
    help="Kunci API dibutuhkan untuk mengaktifkan audit kecerdasan buatan"
)
st.sidebar.markdown(
    "[🔑 Dapatkan API Key Gratis di Google AI Studio](https://aistudio.google.com/)",
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Upload Data")

# Primary File Uploader
uploaded_file = st.sidebar.file_uploader("Upload File CSV Data Iklan Anda", type=["csv"])

df_raw = None

if uploaded_file is not None:
    try:
        df_raw, skipped_lines = read_csv_robust(uploaded_file)
        st.session_state.demo_data_loaded = False
        if skipped_lines > 0:
            st.sidebar.success(f"File berhasil diupload! (Skip {skipped_lines} baris metadata)")
        else:
            st.sidebar.success("File berhasil diupload!")
    except Exception as e:
        st.sidebar.error(f"🚨 Gagal membaca file CSV. Pastikan file Anda terstruktur dengan benar.\n\nDetail Error: {str(e)}")
else:
    st.sidebar.markdown("Belum memiliki file? Gunakan dataset simulasi kami:")
    if st.sidebar.button("Gunakan Data Contoh (Meta Ads)", type="secondary"):
        st.session_state.demo_data_loaded = True
        
    if st.session_state.demo_data_loaded:
        demo_data = {
            'Campaign Name': [
                'Awareness - Cold Traffic Hook A (Hook Jelek)',
                'Retargeting - Product Offer B (Offer Jelek)',
                'Prospecting - Broad CBO Campaign'
            ],
            'Amount Spent': [180.00, 240.00, 350.00],
            'Impressions': [95000, 15000, 48000],
            'Link Clicks': [110, 1150, 680],
            'Conversions': [2, 0, 5],
            'CTR': ['0.12%', '7.67%', '1.42%'],
            'CPC Rata2': [1.64, 0.21, 0.51],
            'Biaya / Konv.': [90.00, 0.00, 70.00],
            'Rasio Konv.': ['1.82%', '0.00%', '0.74%']
        }
        df_raw = pd.DataFrame(demo_data)
        st.sidebar.info("Menggunakan Data Contoh (Meta Ads)")

# App Navigation using Tabs
tab_performance, tab_copywriter, tab_gemini = st.tabs([
    "📊 Performa & Metrik Iklan", 
    "✍️ Psikologi Copywriting", 
    "🤖 Audit AI (Gemini)"
])

# TAB 1: Performance Diagnostics
with tab_performance:
    st.subheader("Laporan Diagnostik Performa Kampanye")
    
    if df_raw is not None:
        # Display Detected Column Mapper (Interactive dropdowns)
        col_exp = st.expander("🔍 Detail Deteksi Kolom & Standardisasi Metrik", expanded=True)
        with col_exp:
            st.markdown("### 🛠️ Manual Column Mapper")
            st.markdown("Cocokkan kolom dari file CSV Anda dengan metrik standar AdDiagnose.AI di bawah ini:")
            
            raw_cols = list(df_raw.columns)
            
            # Fuzzy keywords to calculate default guesses
            campaign_keywords = ['kampanye', 'campaign', 'nama kampanye', 'ad set']
            spend_keywords = ['biaya', 'spend', 'cost', 'nilai', 'jumlah dibelanjakan']
            impressions_keywords = ['ty. iklan', 'impression', 'tayangan', 'tampilan', 'imps', 'imp']
            clicks_keywords = ['klik', 'click']
            conversions_keywords = ['konversi', 'conversion', 'hasil', 'result', 'results', 'purchase', 'pembelian', 'lead']
            ctr_keywords = ['ctr', 'click-through', 'rasio klik']
            cpc_keywords = ['cpc rata2', 'cpc', 'cost per click', 'biaya per klik']
            cpa_keywords = ['biaya / konv.', 'cpa', 'cost per conv', 'cost per conversion', 'biaya per konversi']
            cvr_keywords = ['rasio konv.', 'cvr', 'conversion rate', 'rasio konversi']
            
            # Guess default indices
            idx_camp = guess_default_column(raw_cols, campaign_keywords)
            idx_spend = guess_default_column(raw_cols, spend_keywords, ['click', 'klik', 'impression', 'tayangan', 'tampilan', 'conversion', 'konversi', 'hasil', 'result', 'results', 'ctr', 'cpc', 'cpa', 'cvr'])
            if idx_spend == 0 and not any(k in str(raw_cols[0]).lower() for k in spend_keywords):
                idx_spend = guess_default_column(raw_cols, spend_keywords)
                
            idx_imps = guess_default_column(raw_cols, impressions_keywords, ['click', 'klik', 'conversion', 'konversi', 'hasil', 'result', 'results', 'ctr', 'cpc', 'cpa', 'cvr'])
            if idx_imps == 0 and not any(k in str(raw_cols[0]).lower() for k in impressions_keywords):
                idx_imps = guess_default_column(raw_cols, impressions_keywords)
                
            idx_clicks = guess_default_column(raw_cols, clicks_keywords, ['conversion', 'konversi', 'hasil', 'result', 'results', 'cost', 'spend', 'biaya', 'nilai', 'ctr', 'cpc', 'cpa', 'cvr'])
            if idx_clicks == 0 and not any(k in str(raw_cols[0]).lower() for k in clicks_keywords):
                idx_clicks = guess_default_column(raw_cols, clicks_keywords)
                
            idx_convs = guess_default_column(raw_cols, conversions_keywords, ['cost', 'spend', 'biaya', 'nilai', 'ctr', 'cpc', 'cpa', 'cvr'])
            if idx_convs == 0 and not any(k in str(raw_cols[0]).lower() for k in conversions_keywords):
                idx_convs = guess_default_column(raw_cols, conversions_keywords)
                
            idx_ctr = guess_default_column(raw_cols, ctr_keywords, ['cvr', 'conversion'])
            if idx_ctr == 0 and not any(k in str(raw_cols[0]).lower() for k in ctr_keywords):
                idx_ctr = guess_default_column(raw_cols, ctr_keywords)
                
            idx_cpc = guess_default_column(raw_cols, cpc_keywords, ['cpa', 'conversion'])
            if idx_cpc == 0 and not any(k in str(raw_cols[0]).lower() for k in cpc_keywords):
                idx_cpc = guess_default_column(raw_cols, cpc_keywords)
                
            idx_cpa = guess_default_column(raw_cols, cpa_keywords, ['cpc', 'click'])
            if idx_cpa == 0 and not any(k in str(raw_cols[0]).lower() for k in cpa_keywords):
                idx_cpa = guess_default_column(raw_cols, cpa_keywords)
                
            idx_cvr = guess_default_column(raw_cols, cvr_keywords, ['ctr', 'click'])
            if idx_cvr == 0 and not any(k in str(raw_cols[0]).lower() for k in cvr_keywords):
                idx_cvr = guess_default_column(raw_cols, cvr_keywords)
                
            # Columns select box row layout (3x3 grid)
            c_sel1, c_sel2, c_sel3 = st.columns(3)
            with c_sel1:
                sel_camp = st.selectbox("Pilih Kolom Nama Kampanye:", raw_cols, index=idx_camp, key="manual_sel_camp")
                sel_clicks = st.selectbox("Pilih Kolom Clicks / Klik:", raw_cols, index=idx_clicks, key="manual_sel_clicks")
                sel_cpc = st.selectbox("Pilih Kolom CPC:", raw_cols, index=idx_cpc, key="manual_sel_cpc")
            with c_sel2:
                sel_spend = st.selectbox("Pilih Kolom Biaya / Spend:", raw_cols, index=idx_spend, key="manual_sel_spend")
                sel_convs = st.selectbox("Pilih Kolom Conversions / Konversi:", raw_cols, index=idx_convs, key="manual_sel_convs")
                sel_cpa = st.selectbox("Pilih Kolom CPA / Cost per Conversion:", raw_cols, index=idx_cpa, key="manual_sel_cpa")
            with c_sel3:
                sel_imps = st.selectbox("Pilih Kolom Impressions / Tayangan:", raw_cols, index=idx_imps, key="manual_sel_imps")
                sel_ctr = st.selectbox("Pilih Kolom CTR:", raw_cols, index=idx_ctr, key="manual_sel_ctr")
                sel_cvr = st.selectbox("Pilih Kolom CVR / Conversion Rate:", raw_cols, index=idx_cvr, key="manual_sel_cvr")

        # Process standard columns based on selectbox mappings
        df_standard = pd.DataFrame()
        df_standard['Campaign'] = df_raw[sel_camp].astype(str)
        
        # Helper to clean and convert Spend/CPC/CPA/CTR/CVR to float
        def clean_spend_column(series):
            def clean_val(val):
                if pd.isna(val):
                    return 0.0
                val_str = str(val).strip().replace(' ', '')
                # Strip currency symbols, spaces, percent signs
                val_str = re.sub(r'(?i)rp|\$|eur|â€?|%|Â', '', val_str)
                if not val_str:
                    return 0.0
                
                # Identify punctuation patterns (thousands vs decimal points)
                if '.' in val_str and ',' in val_str:
                    if val_str.find('.') < val_str.find(','):
                        val_str = val_str.replace('.', '').replace(',', '.')
                    else:
                        val_str = val_str.replace(',', '')
                elif ',' in val_str:
                    if val_str.count(',') > 1:
                        val_str = val_str.replace(',', '')
                    else:
                        parts = val_str.split(',')
                        if len(parts[1]) == 3:
                            val_str = val_str.replace(',', '')
                        else:
                            val_str = val_str.replace(',', '.')
                elif '.' in val_str:
                    if val_str.count('.') > 1:
                        val_str = val_str.replace('.', '')
                    else:
                        parts = val_str.split('.')
                        if len(parts[1]) == 3:
                            val_str = val_str.replace('.', '')
                try:
                    return float(val_str)
                except ValueError:
                    return 0.0
                    
            return series.apply(clean_val)

        # Helper to clean and convert integer count fields (digits-only)
        def clean_integer_column(series):
            # Convert series to string, strip whitespace
            cleaned = series.astype(str).str.strip()
            # Regex to keep only digits
            cleaned = cleaned.str.replace(r'[^\d]', '', regex=True)
            # Handle empty values
            cleaned = cleaned.replace('', '0')
            return pd.to_numeric(cleaned, errors='coerce').fillna(0).astype(int)

        # Run cleaning logic only on chosen columns
        df_standard['Spend'] = pd.to_numeric(clean_spend_column(df_raw[sel_spend]), errors='coerce').fillna(0.0)
        df_standard['Impressions'] = clean_integer_column(df_raw[sel_imps])
        df_standard['Clicks'] = clean_integer_column(df_raw[sel_clicks])
        df_standard['Conversions'] = clean_integer_column(df_raw[sel_convs])
        
        # Read ratio fields directly from the mapped columns instead of static formula calculation
        df_standard['CTR (%)'] = clean_spend_column(df_raw[sel_ctr]).fillna(0.0).round(2)
        df_standard['CVR (%)'] = clean_spend_column(df_raw[sel_cvr]).fillna(0.0).round(2)
        df_standard['CPC'] = clean_spend_column(df_raw[sel_cpc]).fillna(0.0).round(2)
        df_standard['CPA'] = clean_spend_column(df_raw[sel_cpa]).fillna(0.0).round(2)
        
        # Sync standardized df to session state for cross-tab access
        st.session_state.df_standard = df_standard
        
        # Summary calculations for overall metrics
        total_spend = df_standard['Spend'].sum()
        total_impressions = df_standard['Impressions'].sum()
        total_clicks = df_standard['Clicks'].sum()
        total_conversions = df_standard['Conversions'].sum()
        
        overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        overall_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        # Format metrics values nicely
        def format_currency(val):
            if "IDR" in currency_choice:
                return f"{currency_symbol}{val:,.0f}"
            else:
                return f"{currency_symbol}{val:,.2f}"

        # Beautiful Custom CSS KPI Metrics Panel
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Spend</div>
                <div class="kpi-value">{format_currency(total_spend)}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Impressions</div>
                <div class="kpi-value">{total_impressions:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Overall CTR</div>
                <div class="kpi-value">{overall_ctr:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Overall CVR</div>
                <div class="kpi-value">{overall_cvr:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Premium Clean Table display
        st.markdown("### 📋 Tabel Summary Metrik Kampanye")
        
        df_display = df_standard.copy()
        
        st.dataframe(
            df_display.style.format({
                'Spend': lambda x: format_currency(x),
                'Impressions': '{:,.0f}',
                'Clicks': '{:,.0f}',
                'Conversions': '{:,.0f}',
                'CTR (%)': '{:.2f}%',
                'CVR (%)': '{:.2f}%',
                'CPC': lambda x: format_currency(x),
                'CPA': lambda x: format_currency(x)
            }),
            use_container_width=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Interactive Plotly Charts
        st.markdown("### 📈 Visualisasi & Analisis Grafik")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            fig_spend_conv = px.bar(
                df_standard,
                x='Campaign',
                y=['Spend', 'Conversions'],
                title='Komparasi Spend vs. Conversions per Kampanye',
                barmode='group',
                color_discrete_sequence=['#8A2387', '#E94057'],
                labels={'value': 'Jumlah', 'variable': 'Metrik'}
            )
            fig_spend_conv.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_family="Outfit",
                title_font_size=18,
                legend_title_text=''
            )
            st.plotly_chart(fig_spend_conv, use_container_width=True)
            
        with chart_col2:
            fig_ctr_cvr = go.Figure()
            fig_ctr_cvr.add_trace(go.Bar(
                x=df_standard['Campaign'],
                y=df_standard['CTR (%)'],
                name='CTR (%)',
                marker_color='#F27121'
            ))
            fig_ctr_cvr.add_trace(go.Bar(
                x=df_standard['Campaign'],
                y=df_standard['CVR (%)'],
                name='CVR (%)',
                marker_color='#ec4899'
            ))
            
            fig_ctr_cvr.update_layout(
                title='CTR vs CVR per Kampanye (%)',
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_family="Outfit",
                title_font_size=18
            )
            st.plotly_chart(fig_ctr_cvr, use_container_width=True)
            
        # Diagnosis Insights Section
        st.markdown("### 💡 Diagnosis & Rekomendasi Kampanye")
        
        for idx, row in df_standard.iterrows():
            ctr = row['CTR (%)']
            cvr = row['CVR (%)']
            camp = row['Campaign']
            
            if ctr >= 1.5 and cvr >= 3.0:
                st.success(f"✅ **{camp}**: Kampanye ini berjalan sangat baik! Baik visual/copywriting (CTR {ctr}%) maupun relevansi landing page (CVR {cvr}%) sangat optimal. Pertahankan dan pertimbangkan menaikkan budget.")
            elif ctr >= 1.5 and cvr < 3.0:
                st.warning(f"⚠️ **{camp}**: Hook iklan sangat berhasil (CTR {ctr}%), tetapi konversinya rendah (CVR {cvr}%). Ada masalah di Landing Page, harga, atau alur pembelian. Perbaiki halaman penawaran Anda!")
            elif ctr < 1.5 and cvr >= 3.0:
                st.info(f"💡 **{camp}**: Audiens yang datang sangat tertarik membeli (CVR {cvr}%), tetapi sangat sedikit orang yang mengklik iklan Anda (CTR {ctr}%). Anda perlu mengganti copywriting atau gambar iklan untuk menarik lebih banyak klik.")
            else:
                st.error(f"🚨 **{camp}**: Performa di bawah rata-rata (CTR {ctr}% & CVR {cvr}%). Kampanye ini memerlukan perombakan menyeluruh baik pada target audiens, kreatif iklan, maupun landing page.")
                
    else:
        st.info("Silakan unggah data CSV Anda atau klik 'Gunakan Data Contoh (Meta Ads)' di sidebar untuk melihat analisis performa iklan.")

# TAB 2: Copywriting Analysis Section (Local + Gemini Diagnosa AI Button)
with tab_copywriter:
    st.subheader("Psikologi Copywriting Diagnoser (Heuristic)")
    st.markdown("Masukkan teks copywriting iklan Anda di bawah ini untuk didiagnosis oleh engine psikologi iklan kami secara lokal.")
    
    copy_input = st.text_area(
        "Teks Copywriting Iklan:",
        value=st.session_state.user_copy_text,
        height=150,
        placeholder="Tulis copywriting iklan Anda di sini...",
        key="copy_text_area"
    )
    
    st.session_state.user_copy_text = copy_input
    
    if copy_input:
        diag = analyze_copywriting(copy_input)
        
        if diag:
            c1, c2, c3 = st.columns(3)
            c1.metric("Jumlah Karakter", diag["char_count"])
            c2.metric("Jumlah Kata", diag["word_count"])
            c3.metric("Jumlah Emoji", diag["emoji_count"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            score_color = diag["rating_color"]
            
            st.markdown(f"""
            <div style="background-color: #111827; padding: 25px; border-radius: 12px; border: 1px solid #374151; text-align: center;">
                <h4 style="margin: 0; color: #9ca3af; font-size: 1rem; font-weight: 500; text-transform: uppercase;">Skor Kualitas Copywriting</h4>
                <div style="font-size: 3.5rem; font-weight: 700; color: {score_color}; margin: 10px 0;">
                    {diag["score"]} / 100
                </div>
                <div style="font-size: 1.2rem; font-weight: 600; color: white;">
                    Kategori: <span style="color: {score_color};">{diag["rating"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_analysis_left, col_analysis_right = st.columns(2)
            
            with col_analysis_left:
                st.markdown("### 🧩 Elemen Psikologi Iklan Terdeteksi")
                
                hook_icon = "✅ Ada" if diag["has_hook"] else "❌ Tidak Ada"
                cta_icon = "✅ Ada" if diag["has_cta"] else "❌ Tidak Ada"
                urgency_icon = "✅ Ada" if diag["has_urgency"] else "❌ Tidak Ada"
                
                st.markdown(f"**1. Hook Pembuka:** {hook_icon}")
                st.markdown(f"**2. Call-To-Action (CTA):** {cta_icon}")
                if diag["found_ctas"]:
                    st.markdown(f"   *Kata terdeteksi: {', '.join([f'`{w}`' for w in diag['found_ctas']])}*")
                    
                st.markdown(f"**3. Elemen Urgensi:** {urgency_icon}")
                if diag["found_urgency"]:
                    st.markdown(f"   *Kata terdeteksi: {', '.join([f'`{w}`' for w in diag['found_urgency']])}*")
                    
            with col_analysis_right:
                st.markdown("### 📋 Rekomendasi Perbaikan")
                if diag["recommendations"]:
                    for rec in diag["recommendations"]:
                        st.markdown(rec)
                else:
                    st.success("🎉 Copywriting Anda sangat seimbang! Memiliki hook pembuka, CTA yang jelas, urgensi, panjang kata ideal, dan emoji penarik perhatian.")

    # Show Gemini AI Diagnosis Button directly under copywriting form if data is successfully loaded
    if st.session_state.df_standard is not None and len(st.session_state.df_standard) > 0:
        st.markdown("---")
        st.subheader("🤖 Diagnosa AI Terintegrasi (Gemini)")
        st.markdown("Hubungkan data metrik di atas dengan copywriting ini secara instan menggunakan AI.")
        
        ready_to_audit = True
        if not gemini_api_key.strip():
            st.info("🔌 Silakan masukkan **Gemini API Key** Anda di sidebar untuk mengaktifkan tombol diagnosa AI.")
            ready_to_audit = False
            
        if ready_to_audit:
            if st.button("Mulai Diagnosa AI 🚀", type="primary", key="diagnose_ai_btn_tab2"):
                with st.spinner("Gemini AI sedang mendiagnosa performa iklan dan copywriting Anda..."):
                    audit_result = audit_ad_creative(
                        api_key=gemini_api_key,
                        df_metrics=st.session_state.df_standard,
                        copy_text=st.session_state.user_copy_text
                    )
                    st.session_state.ai_audit_result = audit_result
                    
            if st.session_state.ai_audit_result:
                st.markdown(f"""
                <div class="ai-box">
                    <div class="ai-header">
                        <span>✨ Hasil Diagnosis Pakar Media Buyer & Psikologi Iklan AI</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(st.session_state.ai_audit_result)


# TAB 3: Gemini AI Audit (Gemini API)
with tab_gemini:
    st.subheader("🤖 AI Ad Creative Audit (Gemini API)")
    st.markdown("Audit copywriting iklan Anda secara komprehensif dengan mengaitkan data performa metrik dari Pandas lokal.")

    ready_to_audit = True
    
    if st.session_state.df_standard is None:
        st.warning("⚠️ File data iklan (CSV) atau Data Contoh belum dimuat.")
        ready_to_audit = False
        
    if not st.session_state.user_copy_text.strip():
        st.warning("⚠️ Teks copywriting iklan di Tab 2 masih kosong.")
        ready_to_audit = False
        
    if not gemini_api_key.strip():
        st.info("🔌 Silakan masukkan **Gemini API Key** Anda pada kolom input di sidebar untuk memulai audit AI.")
        ready_to_audit = False

    if ready_to_audit:
        st.success("✅ Semua data siap dianalisis! Klik tombol di bawah untuk mengaktifkan pakar Media Buyer AI.")
        
        st.markdown(f"**Copywriting yang akan diaudit:**")
        st.info(f"\"{st.session_state.user_copy_text}\"")
        
        if st.button("Mulai Audit dengan Gemini AI 🚀", type="primary", key="audit_ai_btn_tab3"):
            with st.spinner("Gemini AI sedang mengkorelasikan metrik performa lokal Anda dengan psikologi salinan iklan..."):
                audit_result = audit_ad_creative(
                    api_key=gemini_api_key,
                    df_metrics=st.session_state.df_standard,
                    copy_text=st.session_state.user_copy_text
                )
                st.session_state.ai_audit_result = audit_result

        # Display AI Audit Results in a Beautiful Box
        if st.session_state.ai_audit_result:
            st.markdown(f"""
            <div class="ai-box">
                <div class="ai-header">
                    <span>✨ Hasil Diagnosis Pakar Media Buyer & Psikologi Iklan AI</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state.ai_audit_result)
            st.markdown("---")
            st.caption("Analisis di atas dibuat secara langsung oleh model gemini-2.5-flash berdasarkan metrik kampanye terlampir.")
