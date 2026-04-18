import streamlit as st
import pandas as pd
import re
import glob
import unicodedata

st.set_page_config(
    page_title="المعجم اللساني الحاسوبي",
    page_icon="🎓",
    layout="wide"
)

def clean_col(c):
    s = str(c)
    s = unicodedata.normalize('NFKC', s)
    for ch in ['\ufeff', '\u200f', '\u200e', '\u202a', '\u202b', '\u202c', '\u202d', '\u202e']:
        s = s.replace(ch, '')
    return s.strip()

def find_col(df, *candidates):
    if df.empty:
        return None
    cols_clean = {clean_col(c): c for c in df.columns}
    for candidate in candidates:
        target = clean_col(candidate)
        if target in cols_clean:
            return cols_clean[target]
        for clean, original in cols_clean.items():
            if target and (target in clean or clean in target):
                return original
    return None

@st.cache_data
def load_data():
    csv_files = sorted(glob.glob("lexicon_*.csv"))
    if not csv_files:
        return pd.DataFrame(), []
    frames = []
    debug_info = []
    for f in csv_files:
        loaded = False
        for enc in ['utf-8-sig', 'utf-8', 'cp1256', 'windows-1256']:
            for sep in [',', ';', '\t']:
                try:
                    d = pd.read_csv(f, encoding=enc, sep=sep)
                    if len(d.columns) < 2:
                        continue
                    d.columns = [clean_col(c) for c in d.columns]
                    frames.append(d)
                    debug_info.append(f"{f} | ترميز: {enc} | فاصل: {repr(sep)} | أعمدة: {len(d.columns)}")
                    loaded = True
                    break
                except Exception:
                    continue
            if loaded:
                break
        if not loaded:
            debug_info.append(f"{f} | فشل التحميل")
    if not frames:
        return pd.DataFrame(), debug_info
    df = pd.concat(frames, ignore_index=True)
    return df, debug_info

def remove_diacritics(text):
    if pd.isna(text):
        return ""
    arabic_diacritics = re.compile(
        '[\u0617-\u061A\u064B-\u0652\u0656-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED\u0640]'
    )
    return arabic_diacritics.sub('', str(text))

df, debug_info = load_data()

COL_AR = find_col(df, "المصطلح العربي", "المصطلح", "العربي")
COL_EN = find_col(df, "المقابل الإنجليزي", "الإنجليزي", "الانجليزي", "English")
COL_DEF = find_col(df, "التعريف")
COL_ROOT = find_col(df, "الجذر")
COL_POS = find_col(df, "أقسام الكلام", "قسم الكلام", "الوزن")
COL_EX = find_col(df, "المثال")
COL_DEF_SRC = find_col(df, "المصدر التعريف", "مصدر التعريف")
COL_DEF_PG = find_col(df, "صفحة التعريف")
COL_EX_SRC = find_col(df, "المصدر المثال", "مصدر المثال")
COL_EX_PG = find_col(df, "صفحة المثال")

if not df.empty and COL_AR:
    df['__term_clean'] = df[COL_AR].apply(remove_diacritics)
    if COL_DEF:
        df['__def_clean'] = df[COL_DEF].apply(remove_diacritics)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1a2332 0%, #2d4a6e 100%); }
    .main-title { text-align: center; color: #4ecdc4; font-size: 2.5em; font-weight: 900; margin: 25px 0 12px 0; direction: rtl; }
    .subtitle { text-align: center; color: #a8dadc; font-size: 1.1em; margin-bottom: 25px; direction: rtl; }
    .search-container { max-width: 700px; margin: 0 auto 30px auto; }
    .stTextInput > div > div > input { text-align: right; direction: rtl; font-size: 1.15em; padding: 11px 16px; border-radius: 8px; }
    .stButton > button { background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); color: white; font-size: 1.15em; font-weight: 700; padding: 11px 50px; border-radius: 8px; direction: rtl; margin: 0 auto; display: block; }
    .result-card { background: white; padding: 28px; border-radius: 12px; margin: 18px auto; max-width: 850px; border-right: 5px solid #4ecdc4; direction: rtl; text-align: right; }
    .term-header { display: flex; align-items: baseline; gap: 18px; margin-bottom: 10px; flex-wrap: wrap; }
    .term-arabic { color: #1a1a1a; font-size: 1.9em; font-weight: 800; }
    .term-english { color: #4ecdc4; font-size: 1.3em; font-weight: 600; }
    .term-pos { background: #e8f5e9; color: #2e7d32; font-size: 0.95em; font-weight: 600; padding: 3px 14px; border-radius: 15px; margin-right: auto; }
    .term-root { background: #fff3e0; color: #e65100; font-size: 0.95em; font-weight: 600; padding: 3px 14px; border-radius: 15px; }
    .section-title { color: #2c3e50; font-size: 1.05em; font-weight: 700; margin: 13px 0 7px 0; }
    .term-definition { color: #444; font-size: 1.1em; line-height: 1.85; padding: 14px; background: #f8f9fa; border-radius: 7px; margin-bottom: 11px; }
    .term-example { color: #555; font-size: 1.02em; line-height: 1.75; padding: 11px; background: #e9ecef; border-radius: 6px; margin-bottom: 11px; font-style: italic; }
    .source-box { background: #f1f3f5; padding: 9px 11px; border-radius: 5px; font-size: 0.88em; color: #666; margin: 7px 0; }
    .empty-state { text-align: center; padding: 55px 18px; color: #a8dadc; direction: rtl; }
    .empty-state-icon { font-size: 3.5em; margin-bottom: 18px; }
    .empty-state-text { font-size: 1.25em; margin-bottom: 9px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">المُعْجَمُ اللِّسَانِيُّ الْحَاسُوبِيُّ</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">مُعْجَمٌ عَرَبِيٌّ-إِنْجِلِيزِيٌّ لِلْمُصْطَلَحَاتِ اللِّسَانِيَّةِ الْحَاسُوبِيَّةِ</div>', unsafe_allow_html=True)

if df.empty:
    st.error("لَمْ يُتِمَّ الْعُثُورُ عَلَى أَيِّ مَلَفٍّ بِاسْمِ lexicon_*.csv")
    st.write("**مَعْلُومَاتُ التَّشْخِيصِ:**")
    for info in debug_info:
        st.text(info)
    st.stop()

if not COL_AR or not COL_EN:
    st.error("❌ الْأَعْمِدَةُ الْمَوْجُودَةُ فِي مِلَفِّكَ لَا تُطَابِقُ الْمُتَوَقَّعَةَ")
    st.write("**الْأَعْمِدَةُ الْمَوْجُودَةُ فِعْلًا فِي الْمِلَفِّ:**")
    for c in df.columns:
        st.code(repr(c))
    st.write("**مَعْلُومَاتُ التَّحْمِيلِ:**")
    for info in debug_info:
        st.text(info)
    st.stop()

st.markdown('<div class="search-container">', unsafe_allow_html=True)
search = st.text_input("بحث", placeholder="ابْحَثْ عَنْ مُصْطَلَحٍ...", label_visibility="collapsed")
col1, col2 = st.columns([1, 1])
with col1:
    search_button = st.button("بَحْثٌ")
with col2:
    deep_search = st.checkbox("بَحْثٌ فِي التَّعْرِيفِ أَيْضًا")
st.markdown('</div>', unsafe_allow_html=True)

def sg(row, col):
    if col and col in row.index and pd.notna(row[col]) and str(row[col]).strip():
        return str(row[col]).strip()
    return ""

if search_button or search:
    if search:
        search_clean = remove_diacritics(search)
        mask = (
            df['__term_clean'].str.contains(search_clean, na=False, case=False) |
            df[COL_EN].astype(str).str.contains(search, na=False, case=False)
        )
        if deep_search and '__def_clean' in df.columns:
            mask = mask | df['__def_clean'].str.contains(search_clean, na=False, case=False)
        results = df[mask]

        if not results.empty:
            st.success(f"عُثِرَ عَلَى {len(results)} نَتِيجَةٍ")
            for _, row in results.iterrows():
                html = '<div class="result-card"><div class="term-header">'
                html += f'<span class="term-arabic">{sg(row, COL_AR)}</span>'
                html += f'<span class="term-english">{sg(row, COL_EN)}</span>'
                pos = sg(row, COL_POS)
                if pos:
                    html += f'<span class="term-pos">{pos}</span>'
                root = sg(row, COL_ROOT)
                if root:
                    html += f'<span class="term-root">{root}</span>'
                html += '</div>'

                definition = sg(row, COL_DEF)
                if definition:
                    html += '<div class="section-title">التَّعْرِيفُ:</div>'
                    html += f'<div class="term-definition">{definition}</div>'

                def_source = sg(row, COL_DEF_SRC)
                def_page = sg(row, COL_DEF_PG)
                if def_source:
                    s = def_source + (f'، ص {def_page}' if def_page else '')
                    html += f'<div class="source-box">{s}</div>'

                example = sg(row, COL_EX)
                if example:
                    html += '<div class="section-title">مِثَالٌ:</div>'
                    html += f'<div class="term-example">{example}</div>'
                    ex_source = sg(row, COL_EX_SRC) or def_source
                    ex_page = sg(row, COL_EX_PG) or def_page
                    if ex_source:
                        s = ex_source + (f'، ص {ex_page}' if ex_page else '')
                        html += f'<div class="source-box">{s}</div>'

                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("لَمْ يُعْثَرْ عَلَى نَتَائِجَ. جَرِّبْ كَلِمَاتٍ أُخْرَى.")
    else:
        st.warning("الرَّجَاءُ كِتَابَةُ مُصْطَلَحٍ")
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <div class="empty-state-text">ابْدَأِ الْبَحْثَ لِاسْتِكْشَافِ الْمُعْجَمِ</div>
        <div style="font-size: 1.05em; color: #6c757d; margin-top: 9px;">
            اكْتُبْ مُصْطَلَحًا عَرَبِيًّا أَوْ إِنْجِلِيزِيًّا فِي حَقْلِ الْبَحْثِ
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('''
<div style="text-align: center; color: #a8dadc; padding: 28px 18px; direction: rtl; margin-top: 35px; border-top: 1px solid rgba(168, 218, 220, 0.3);">
    <div style="font-size: 1.15em; font-weight: 700; color: #4ecdc4; margin-bottom: 7px;">مَعْهَدُ الدَّوْحَةِ لِلدِّرَاسَاتِ الْعُلْيَا</div>
    <div style="font-size: 0.95em;">الْمُعْجَمُ اللِّسَانِيُّ الْحَاسُوبِيُّ</div>
    <div style="font-size: 0.85em; color: #f0ad4e; margin-top: 10px;">⚙️ هٰذَا الْمُعْجَمُ فِي طَوْرِ التَّطْوِيرِ الْمُسْتَمِرِّ</div>
</div>
''', unsafe_allow_html=True)
