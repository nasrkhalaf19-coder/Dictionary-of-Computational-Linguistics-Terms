import streamlit as st
import pandas as pd
import re
import glob

st.set_page_config(
    page_title="المعجم اللساني الحاسوبي",
    page_icon="🎓",
    layout="wide"
)

@st.cache_data
def load_data():
    csv_files = sorted(glob.glob("lexicon_*.csv"))
    if not csv_files:
        return pd.DataFrame()
    frames = []
    for f in csv_files:
        try:
            frames.append(pd.read_csv(f, encoding='utf-8-sig'))
        except Exception:
            try:
                frames.append(pd.read_csv(f, encoding='utf-8'))
            except Exception:
                pass
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df.columns = [c.strip() for c in df.columns]
    if "المقابل الإنجليزي" in df.columns:
        df = df.drop_duplicates(subset=["المقابل الإنجليزي"], keep="last")
    return df

def remove_diacritics(text):
    if pd.isna(text):
        return ""
    arabic_diacritics = re.compile(
        '[\u0617-\u061A\u064B-\u0652\u0656-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED\u0640]'
    )
    return arabic_diacritics.sub('', str(text))

df = load_data()
if not df.empty:
    df['المصطلح_بدون_تشكيل'] = df['المصطلح العربي'].apply(remove_diacritics)
    if 'التعريف' in df.columns:
        df['التعريف_بدون_تشكيل'] = df['التعريف'].apply(remove_diacritics)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a2332 0%, #2d4a6e 100%);
    }
    .main-title {
        text-align: center;
        color: #4ecdc4;
        font-size: 2.5em;
        font-weight: 900;
        margin: 25px 0 12px 0;
        direction: rtl;
    }
    .subtitle {
        text-align: center;
        color: #a8dadc;
        font-size: 1.1em;
        margin-bottom: 25px;
        direction: rtl;
    }
    .search-container {
        max-width: 700px;
        margin: 0 auto 30px auto;
    }
    .stTextInput > div > div > input {
        text-align: right;
        direction: rtl;
        font-size: 1.15em;
        padding: 11px 16px;
        border-radius: 8px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
        font-size: 1.15em;
        font-weight: 700;
        padding: 11px 50px;
        border-radius: 8px;
        direction: rtl;
        margin: 0 auto;
        display: block;
    }
    .result-card {
        background: white;
        padding: 28px;
        border-radius: 12px;
        margin: 18px auto;
        max-width: 850px;
        border-right: 5px solid #4ecdc4;
        direction: rtl;
        text-align: right;
    }
    .term-header {
        display: flex;
        align-items: baseline;
        gap: 18px;
        margin-bottom: 10px;
        flex-wrap: wrap;
    }
    .term-arabic {
        color: #1a1a1a;
        font-size: 1.9em;
        font-weight: 800;
    }
    .term-english {
        color: #4ecdc4;
        font-size: 1.3em;
        font-weight: 600;
    }
    .term-pos {
        background: #e8f5e9;
        color: #2e7d32;
        font-size: 0.95em;
        font-weight: 600;
        padding: 3px 14px;
        border-radius: 15px;
        margin-right: auto;
    }
    .term-root {
        background: #fff3e0;
        color: #e65100;
        font-size: 0.95em;
        font-weight: 600;
        padding: 3px 14px;
        border-radius: 15px;
    }
    .section-title {
        color: #2c3e50;
        font-size: 1.05em;
        font-weight: 700;
        margin: 13px 0 7px 0;
    }
    .term-definition {
        color: #444;
        font-size: 1.1em;
        line-height: 1.85;
        padding: 14px;
        background: #f8f9fa;
        border-radius: 7px;
        margin-bottom: 11px;
    }
    .term-example {
        color: #555;
        font-size: 1.02em;
        line-height: 1.75;
        padding: 11px;
        background: #e9ecef;
        border-radius: 6px;
        margin-bottom: 11px;
        font-style: italic;
    }
    .source-box {
        background: #f1f3f5;
        padding: 9px 11px;
        border-radius: 5px;
        font-size: 0.88em;
        color: #666;
        margin: 7px 0;
    }
    .empty-state {
        text-align: center;
        padding: 55px 18px;
        color: #a8dadc;
        direction: rtl;
    }
    .empty-state-icon {
        font-size: 3.5em;
        margin-bottom: 18px;
    }
    .empty-state-text {
        font-size: 1.25em;
        margin-bottom: 9px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">المُعْجَمُ اللِّسَانِيُّ الْحَاسُوبِيُّ</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">مُعْجَمٌ عَرَبِيٌّ-إِنْجِلِيزِيٌّ لِلْمُصْطَلَحَاتِ اللِّسَانِيَّةِ الْحَاسُوبِيَّةِ</div>', unsafe_allow_html=True)

st.markdown('<div class="search-container">', unsafe_allow_html=True)
search = st.text_input("بحث", placeholder="ابْحَثْ عَنْ مُصْطَلَحٍ...", label_visibility="collapsed")
col1, col2 = st.columns([1, 1])
with col1:
    search_button = st.button("بَحْثٌ")
with col2:
    deep_search = st.checkbox("بَحْثٌ فِي التَّعْرِيفِ أَيْضًا")
st.markdown('</div>', unsafe_allow_html=True)

def safe_get(row, col):
    if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
        return str(row[col]).strip()
    return ""

if df.empty:
    st.warning("لَا تُوجَدُ بَيَانَاتٌ. تَأَكَّدْ مِنْ وُجُودِ مَلَفَّاتِ lexicon_*.csv")
elif search_button or search:
    if search:
        search_clean = remove_diacritics(search)
        mask = (
            df["المصطلح_بدون_تشكيل"].str.contains(search_clean, na=False, case=False) |
            df["المقابل الإنجليزي"].str.contains(search, na=False, case=False)
        )
        if deep_search and 'التعريف_بدون_تشكيل' in df.columns:
            mask = mask | df["التعريف_بدون_تشكيل"].str.contains(search_clean, na=False, case=False)
        results = df[mask]

        if not results.empty:
            st.success(f"عُثِرَ عَلَى {len(results)} نَتِيجَةٍ")
            for _, row in results.iterrows():
                html = '<div class="result-card">'
                html += '<div class="term-header">'
                html += f'<span class="term-arabic">{safe_get(row, "المصطلح العربي")}</span>'
                html += f'<span class="term-english">{safe_get(row, "المقابل الإنجليزي")}</span>'

                pos = safe_get(row, "أقسام الكلام")
                if pos:
                    html += f'<span class="term-pos">{pos}</span>'

                root = safe_get(row, "الجذر")
                if root:
                    html += f'<span class="term-root">{root}</span>'

                html += '</div>'

                definition = safe_get(row, "التعريف")
                if definition:
                    html += '<div class="section-title">التَّعْرِيفُ:</div>'
                    html += f'<div class="term-definition">{definition}</div>'

                def_source = safe_get(row, "المصدر التعريف")
                def_page = safe_get(row, "صفحة التعريف")
                if def_source:
                    s = def_source
                    if def_page:
                        s += f'، ص {def_page}'
                    html += f'<div class="source-box">{s}</div>'

                example = safe_get(row, "المثال")
                if example:
                    html += '<div class="section-title">مِثَالٌ:</div>'
                    html += f'<div class="term-example">{example}</div>'

                    ex_source = safe_get(row, "المصدر المثال") or def_source
                    ex_page = safe_get(row, "صفحة المثال") or def_page
                    if ex_source:
                        s = ex_source
                        if ex_page:
                            s += f'، ص {ex_page}'
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
