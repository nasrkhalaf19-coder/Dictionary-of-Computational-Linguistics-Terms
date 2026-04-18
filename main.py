import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="المعجم اللساني الحاسوبي",
    page_icon="🎓",
    layout="wide"
)

@st.cache_data
def load_data():
    import glob
    csv_files = sorted(glob.glob("lexicon_*.csv"))
    if not csv_files:
        return pd.DataFrame()
    frames = []
    for f in csv_files:
        try:
            frames.append(pd.read_csv(f, encoding='utf-8'))
        except Exception:
            pass
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(subset=["المقابل الإنجليزي"], keep="last")
    # تسجيل أسماء الملفات المحمّلة
    st.session_state['loaded_files'] = [f.replace('lexicon_', '').replace('.csv', '') for f in csv_files]
    return df

def remove_diacritics(text):
    if pd.isna(text):
        return ""
    arabic_diacritics = re.compile("""
                             ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    return arabic_diacritics.sub('', str(text))

df = load_data()
df['المصطلح_بدون_تشكيل'] = df['المصطلح العربي'].apply(remove_diacritics)
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
search_button = st.button("بَحْثٌ")
st.markdown('</div>', unsafe_allow_html=True)

if search_button or search:
    if search:
        search_clean = remove_diacritics(search)

        results = df[
            df["المصطلح_بدون_تشكيل"].str.contains(search_clean, na=False, case=False) |
            df["المقابل الإنجليزي"].str.contains(search, na=False, case=False) |
            df["التعريف_بدون_تشكيل"].str.contains(search_clean, na=False, case=False)
        ]

        if not results.empty:
            st.success(f"عُثِرَ عَلَى {len(results)} نَتِيجَةٍ")

            for _, row in results.iterrows():
                html = '<div class="result-card">'
                html += '<div class="term-header">'
                html += f'<span class="term-arabic">{row["المصطلح العربي"]}</span>'
                html += f'<span class="term-english">{row["المقابل الإنجليزي"]}</span>'

                # قسم الكلام والوزن - بعيداً عن المصطلح
                info_parts = []
                if pd.notna(row["الوزن"]) and str(row["الوزن"]).strip():
                    info_parts.append(row["الوزن"])
                if pd.notna(row["معلومات إضافية"]) and str(row["معلومات إضافية"]).strip():
                    info_parts.append(row["معلومات إضافية"])
                if info_parts:
                    html += f'<span class="term-pos">{" | ".join(info_parts)}</span>'

                # الجذر - بعيداً عن المصطلح
                if pd.notna(row["الجذر"]) and str(row["الجذر"]).strip():
                    html += f'<span class="term-root">{row["الجذر"]}</span>'

                html += '</div>'

                html += '<div class="section-title">التَّعْرِيفُ:</div>'
                html += f'<div class="term-definition">{row["التعريف"]}</div>'

                if pd.notna(row["المصدر التعريف"]) and str(row["المصدر التعريف"]).strip():
                    source = f'{row["المصدر التعريف"]}'
                    if pd.notna(row["صفحة التعريف"]) and str(row["صفحة التعريف"]).strip():
                        source += f'، ص {row["صفحة التعريف"]}'
                    html += f'<div class="source-box">{source}</div>'

                if pd.notna(row["المثال"]) and str(row["المثال"]).strip():
                    html += '<div class="section-title">مِثَالٌ:</div>'
                    html += f'<div class="term-example">{row["المثال"]}</div>'

                    # إذا كان مصدر المثال فارغاً، يُنسخ تلقائياً من مصدر التعريف
                    ex_source = row["المصدر المثال"] if pd.notna(row["المصدر المثال"]) and str(row["المصدر المثال"]).strip() else row.get("المصدر التعريف", "")
                    ex_page = row["صفحة المثال"] if pd.notna(row["صفحة المثال"]) and str(row["صفحة المثال"]).strip() else row.get("صفحة التعريف", "")

                    if pd.notna(ex_source) and str(ex_source).strip():
                        example_source = f'{ex_source}'
                        if pd.notna(ex_page) and str(ex_page).strip():
                            example_source += f'، ص {ex_page}'
                        html += f'<div class="source-box">{example_source}</div>'

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
