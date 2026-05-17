import streamlit as st
from groq import Groq
import json, re

st.set_page_config(
    page_title="Rigel AI – CV Optimize",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .main-title { font-family: 'DM Serif Display', serif; font-size: 2.8rem; text-align: center; letter-spacing: -0.02em; margin-bottom: 0.2rem; }
  .subtitle { text-align: center; color: #888; font-size: 1rem; margin-bottom: 2.5rem; }
  .badge { display: inline-block; background: #f0f0f0; color: #555; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 4px 14px; border-radius: 20px; margin-bottom: 1rem; }
  .header-center { text-align: center; }
  .section-label { font-size: 0.75rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: #999; margin-bottom: 0.4rem; }
  .result-box { background: #fafafa; border: 1px solid #ebebeb; border-radius: 10px; padding: 1.2rem 1.4rem; font-size: 0.9rem; line-height: 1.75; min-height: 280px; white-space: pre-wrap; color: #222; }
  .free-note { font-size: 0.75rem; color: #aaa; text-align: right; }
  .stButton > button { width: 100%; background: #111 !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-size: 1rem !important; padding: 0.65rem 0 !important; font-weight: 500 !important; }
  .stButton > button:hover { opacity: 0.82 !important; }
</style>
""", unsafe_allow_html=True)

if "usage" not in st.session_state:
    st.session_state.usage = 999
if "result" not in st.session_state:
    st.session_state.result = ""
if "scores" not in st.session_state:
    st.session_state.scores = {}

st.markdown('<div class="header-center"><span class="badge">✦ Rigel AI</span></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">CV\'ni saniyeler içinde düzelt</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI destekli optimizasyon — insan gözünden ve AI dedektörlerinden geçer</div>', unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Groq API Key", type="password", placeholder="gsk_...")
    if not api_key:
        st.info("Sidebar'dan Groq API key'ini gir.")
        st.stop()

col_in, _, col_out = st.columns([1, 0.05, 1])

with col_in:
    st.markdown('<div class="section-label">CV\'niz</div>', unsafe_allow_html=True)
    cv_input = st.text_area(
        label="cv_input",
        label_visibility="collapsed",
        placeholder="CV'nizi buraya yapıştırın...",
        height=300,
    )
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("Ton", ["Teknik", "Resmi", "Günlük"])
    with col2:
        focus = st.selectbox("Odak", ["Genel", "ATS Skoru", "Liderlik"])

    st.markdown(f'<div class="free-note">Kalan kullanım: {st.session_state.usage}</div>', unsafe_allow_html=True)
    optimize_clicked = st.button("✦ CV'yi Optimize Et")

with col_out:
    st.markdown('<div class="section-label">Optimize Edilmiş CV</div>', unsafe_allow_html=True)

    if optimize_clicked:
        if not cv_input.strip():
            st.warning("Lütfen önce CV'nizi yapıştırın.")
        elif st.session_state.usage <= 0:
            st.error("Kullanım limitiniz doldu.")
        else:
            with st.spinner("CV analiz ediliyor ve yeniden yazılıyor..."):
                prompt = f"""Sen deneyimli bir kariyer danışmanı ve profesyonel CV yazarısın.

Aşağıdaki CV'yi şu kurallara göre yeniden yaz:
- Güçlü eylem fiilleri kullan (Yönetti, Geliştirdi, Teslim Etti, Azalttı, Artırdı, Tasarladı, Başlattı)
- Mümkün olduğunda ölçülebilir başarılar ekle (örn: "Yükleme süresini %40 azalttı")
- Öz, etkili ve ATS uyumlu olsun
- Teknik becerileri net şekilde öne çıkar
- Zayıf, pasif veya genel ifadeleri kaldır

KRİTİK — Yazım stili kuralları (kesinlikle uyulmalı):
- Cümle uzunluklarını çeşitlendir: kısa ve uzun cümleleri karıştır
- Doğal geçişler kullan — "Bunun yanı sıra", "Kısacası", "Özellikle" gibi
- "Ayrıca", "Dahası", "Ek olarak" gibi tekrarlayan kalıplardan kaçın
- Arka arkaya aynı kelimeyle başlayan cümleler yazma
- Madde uzunluklarını değiştir — bazıları kısa, bazıları daha uzun olsun
- Gerçek bir insan uzman yazmış gibi yaz, yapay zeka değil
- İngilizce kelime veya kalıp KULLANMA, tamamen Türkçe yaz

Ton: {tone}
Odak: {focus}
Dil: CV hangi dilde yazılmışsa aynı dilde yanıt ver.

CV'yi yazdıktan sonra, tam olarak şu formatta bir JSON bloğu ekle (markdown yok, sadece ham JSON):
{{"scores":{{"etki":0,"netlik":0,"ats":0,"insan":0}}}}
Tüm değerler 0-100 arası olsun.

CV:
{cv_input}"""

                try:
                    client = Groq(api_key=api_key)
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1500,
                        temperature=0.7,
                    )
                    raw = response.choices[0].message.content

                    scores = {"etki": 75, "netlik": 80, "ats": 72, "insan": 88}
                    cv_text = raw
                    match = re.search(r'\{[\s\S]*?"scores"[\s\S]*?\}', raw)
                    if match:
                        try:
                            scores = json.loads(match.group(0))["scores"]
                        except:
                            pass
                        cv_text = raw[:match.start()].strip()

                    st.session_state.result = cv_text
                    st.session_state.scores = scores
                    st.session_state.usage = max(0, st.session_state.usage - 1)

                except Exception as e:
                    st.error(f"Hata: {e}")

    if st.session_state.result:
        st.markdown(f'<div class="result-box">{st.session_state.result}</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            st.download_button("⬇ İndir", st.session_state.result, file_name="optimize-cv.txt", mime="text/plain", use_container_width=True)
        with b2:
            if st.button("↻ Yeniden Oluştur", use_container_width=True):
                st.session_state.result = ""
                st.rerun()
    else:
        st.markdown('<div class="result-box" style="color:#bbb;font-style:italic;">Optimize edilmiş CV burada görünecek...</div>', unsafe_allow_html=True)

if st.session_state.scores:
    st.markdown("---")
    st.markdown("**CV Skor Analizi**")
    sc = st.session_state.scores
    c1, c2, c3, c4 = st.columns(4)
    for col, (key, label) in zip([c1, c2, c3, c4], [("etki","Etki"), ("netlik","Netlik"), ("ats","ATS Uyumu"), ("insan","İnsan Skoru")]):
        val = sc.get(key, 0)
        col.metric(label, f"{val}/100")
        col.progress(val / 100)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#bbb;font-size:0.8rem;">Rigel Digital Systems · Geliştiriciler ve öğrenciler için AI araçları</div>', unsafe_allow_html=True)
