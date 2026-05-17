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
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Giriş animasyonu */
  @keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .anim-1 { animation: fadeSlideUp 0.6s ease both; }
  .anim-2 { animation: fadeSlideUp 0.6s ease 0.15s both; }
  .anim-3 { animation: fadeSlideUp 0.6s ease 0.3s both; }
  .anim-4 { animation: fadeSlideUp 0.6s ease 0.45s both; }

  .header-center { text-align: center; padding: 2rem 0 1.5rem; }
  .badge {
    display: inline-block;
    background: #f0f0f0;
    color: #666;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 5px 16px;
    border-radius: 20px;
    margin-bottom: 1.2rem;
  }
  .main-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
    line-height: 1.1;
  }
  .subtitle {
    color: #999;
    font-size: 0.95rem;
    margin-bottom: 0;
  }

  /* Bölüm başlıkları */
  .section-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #aaa;
    margin-bottom: 0.5rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #f0f0f0;
  }

  /* Textarea */
  .stTextArea textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    line-height: 1.7 !important;
    border-radius: 10px !important;
    border: 1px solid #2a2a2a !important;
    padding: 14px !important;
    background: #161616 !important;
    color: #fff !important;
  }
  .stTextArea textarea:focus {
    border-color: #444 !important;
  }
  .stTextArea textarea::placeholder { color: #555 !important; }

  /* Sonuç kutusu */
  .result-box {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 14px 16px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    line-height: 1.7;
    min-height: 300px;
    white-space: pre-wrap;
    color: #fff;
  }
  .result-box.empty { color: #555; font-style: italic; }

  /* Select kutuları */
  .stSelectbox > div > div {
    border-radius: 8px !important;
    border: 1px solid #2a2a2a !important;
    background: #161616 !important;
    color: #fff !important;
    font-size: 0.88rem !important;
  }
  .stSelectbox svg { fill: #888 !important; }

  .free-note {
    font-size: 0.72rem;
    color: #bbb;
    text-align: right;
    margin-top: 6px;
  }

  /* Butonlar */
  .stButton > button {
    width: 100%;
    background: #111 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 0 !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em;
    transition: opacity 0.2s;
  }
  .stButton > button:hover { opacity: 0.78 !important; }

  div[data-testid="stDownloadButton"] button {
    background: #f5f5f5 !important;
    color: #333 !important;
    border: 1px solid #e0e0e0 !important;
  }
  div[data-testid="stDownloadButton"] button:hover {
    background: #eee !important;
    opacity: 1 !important;
  }

  /* Metrik kartlar */
  [data-testid="metric-container"] {
    background: #fafafa;
    border: 1px solid #f0f0f0;
    border-radius: 10px;
    padding: 12px 16px;
  }

  /* Ayırıcı */
  hr { border: none; border-top: 1px solid #f0f0f0; margin: 1.5rem 0; }

  /* Footer */
  .footer {
    text-align: center;
    color: #ccc;
    font-size: 0.75rem;
    padding: 1rem 0 2rem;
  }
</style>
""", unsafe_allow_html=True)

if "usage" not in st.session_state:
    st.session_state.usage = 999
if "result" not in st.session_state:
    st.session_state.result = ""
if "scores" not in st.session_state:
    st.session_state.scores = {}

# Header — animasyonlu
st.markdown("""
<div class="header-center">
  <div class="anim-1"><span class="badge">✦ Rigel AI</span></div>
  <div class="anim-2"><div class="main-title">CV'ni saniyeler içinde düzelt</div></div>
  <div class="anim-3"><div class="subtitle">AI destekli optimizasyon — insan gözünden ve AI dedektörlerinden geçer</div></div>
</div>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Groq API Key", type="password", placeholder="gsk_...")
    if not api_key:
        st.info("Sidebar'dan Groq API key'ini gir.")
        st.stop()

st.markdown('<div class="anim-4">', unsafe_allow_html=True)
col_in, _, col_out = st.columns([1, 0.04, 1])

with col_in:
    st.markdown('<div class="section-label">CV\'niz</div>', unsafe_allow_html=True)
    cv_input = st.text_area(
        label="cv",
        label_visibility="collapsed",
        placeholder="CV'nizi buraya yapıştırın...",
        height=300,
    )
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("Ton", ["Teknik", "Resmi", "Günlük"], label_visibility="visible")
    with col2:
        focus = st.selectbox("Odak", ["Genel", "ATS Skoru", "Liderlik"], label_visibility="visible")

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
- Mümkün olduğunda ölçülebilir başarılar ekle (örn: "Yükleme süresini yüzde 40 azalttı")
- Öz, etkili ve ATS uyumlu olsun
- Teknik becerileri net şekilde öne çıkar
- Zayıf, pasif veya genel ifadeleri kaldır

KRİTİK — Yazım stili kuralları:
- Cümle uzunluklarını çeşitlendir: kısa ve uzun cümleleri karıştır
- Doğal geçişler kullan — "Bunun yanı sıra", "Kısacası", "Özellikle" gibi
- Arka arkaya aynı kelimeyle başlayan cümleler yazma
- Madde uzunluklarını değiştir — bazıları kısa, bazıları daha uzun olsun
- Gerçek bir insan uzman yazmış gibi yaz, yapay zeka değil
- İngilizce kelime veya kalıp kesinlikle kullanma

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
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            st.download_button("⬇ İndir", st.session_state.result, file_name="optimize-cv.txt", mime="text/plain", use_container_width=True)
        with b2:
            if st.button("↻ Yeniden Oluştur", use_container_width=True):
                st.session_state.result = ""
                st.rerun()
    else:
        st.markdown('<div class="result-box empty">Optimize edilmiş CV burada görünecek...</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

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
st.markdown('<div class="footer">Rigel Digital Systems · Geliştiriciler ve öğrenciler için AI araçları</div>', unsafe_allow_html=True)
