import streamlit as st
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IntelliLoan · AI Loan Approval",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{--navy:#0d1b2a;--teal:#1b998b;--gold:#e9c46a;--light:#f4f9fb;--danger:#e63946;--success:#2dc653;--card-bg:#ffffff;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:var(--light);}
.hero{background:linear-gradient(135deg,var(--navy) 0%,#1a2f45 60%,#0f3460 100%);border-radius:20px;padding:40px 48px;margin-bottom:32px;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:300px;height:300px;background:radial-gradient(circle,rgba(27,153,139,.35) 0%,transparent 70%);border-radius:50%;}
.hero-title{font-family:'Playfair Display',serif;font-size:2.8rem;font-weight:900;color:#fff;margin:0 0 8px;letter-spacing:-.5px;}
.hero-title span{color:var(--gold);}
.hero-subtitle{color:rgba(255,255,255,.7);font-size:1.05rem;font-weight:300;margin:0;}
.hero-badge{display:inline-block;background:var(--teal);color:#fff;border-radius:50px;padding:4px 14px;font-size:.75rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:16px;}
.card{background:var(--card-bg);border-radius:16px;padding:28px 32px;box-shadow:0 2px 16px rgba(13,27,42,.07);border:1px solid rgba(13,27,42,.07);margin-bottom:20px;}
.card-title{font-family:'Playfair Display',serif;font-size:1.25rem;color:var(--navy);font-weight:700;margin-bottom:18px;padding-bottom:12px;border-bottom:2px solid var(--gold);display:flex;align-items:center;gap:8px;}
.result-approved{background:linear-gradient(135deg,#0d2e1a 0%,#0a3d22 100%);border:2px solid var(--success);border-radius:16px;padding:32px;text-align:center;color:#fff;}
.result-rejected{background:linear-gradient(135deg,#2e0d0d 0%,#3d0a0a 100%);border:2px solid var(--danger);border-radius:16px;padding:32px;text-align:center;color:#fff;}
.result-icon{font-size:3rem;margin-bottom:8px;}
.result-label{font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;margin:0;}
.result-prob{font-size:1rem;color:rgba(255,255,255,.75);margin-top:6px;}
.prob-bar-wrap{margin-top:20px;}
.prob-bar-bg{background:rgba(255,255,255,.15);border-radius:50px;height:10px;overflow:hidden;margin:6px 0 12px;}
.prob-bar-fill{height:100%;border-radius:50px;}
[data-testid="stSidebar"]{background:var(--navy)!important;}
[data-testid="stSidebar"] *{color:rgba(255,255,255,.85)!important;}
div.stButton>button{background:linear-gradient(135deg,var(--teal) 0%,#13756a 100%);color:white;border:none;border-radius:12px;padding:14px 32px;font-size:1rem;font-weight:600;width:100%;margin-top:8px;font-family:'DM Sans',sans-serif;}
div.stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(27,153,139,.4);}
.chat-bubble-user{background:var(--navy);color:#fff;border-radius:18px 18px 4px 18px;padding:12px 18px;margin:8px 0 8px auto;max-width:75%;font-size:.9rem;}
.chat-bubble-bot{background:#fff;color:var(--navy);border-radius:18px 18px 18px 4px;padding:12px 18px;margin:8px auto 8px 0;max-width:80%;font-size:.9rem;border:1px solid rgba(13,27,42,.1);}
.chat-wrap{max-height:380px;overflow-y:auto;padding:8px 4px;}
.tip{background:rgba(27,153,139,.08);border-left:4px solid var(--teal);border-radius:0 12px 12px 0;padding:12px 16px;font-size:.88rem;color:var(--navy);margin:10px 0;}
.field-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(13,27,42,.06);}
.field-label{color:#555;font-size:.85rem;font-weight:500;}
.field-value{color:var(--navy);font-size:.9rem;font-weight:600;}
.field-note{color:#888;font-size:.75rem;font-weight:400;margin-left:6px;}
.nlp-badge{display:inline-block;background:rgba(27,153,139,.12);color:var(--teal);border:1px solid var(--teal);border-radius:6px;padding:2px 10px;font-size:.75rem;font-weight:600;margin-left:8px;}
.doc-drop{border:2px dashed var(--teal);border-radius:16px;padding:40px;text-align:center;background:rgba(27,153,139,.04);}
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

# ── Helpers ───────────────────────────────────────────────────────────────────
def call_predict(payload):
    try:
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def call_predict_document(file_bytes, filename):
    try:
        r = requests.post(
            f"{API_URL}/predict-document",
            files={"file": (filename, file_bytes, "application/pdf")},
            timeout=15
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def render_result(result):
    approved = result.get("approved", False)
    prob_yes = result.get("approval_probability", 0)
    prob_no  = result.get("rejection_probability", 0)
    css = "result-approved" if approved else "result-rejected"
    icon  = "✅" if approved else "❌"
    label = "LOAN APPROVED" if approved else "LOAN REJECTED"
    color = "#2dc653" if approved else "#e63946"
    st.markdown(f"""
    <div class="{css}">
      <div class="result-icon">{icon}</div>
      <p class="result-label">{label}</p>
      <p class="result-prob">Confidence: {prob_yes if approved else prob_no:.1f}%</p>
      <div class="prob-bar-wrap">
        <small style="color:rgba(255,255,255,.6)">Approval probability</small>
        <div class="prob-bar-bg">
          <div class="prob-bar-fill" style="width:{prob_yes}%;background:{color};"></div>
        </div>
        <small style="color:rgba(255,255,255,.5)">{prob_yes:.1f}% approved &nbsp;·&nbsp; {prob_no:.1f}% rejected</small>
      </div>
    </div>""", unsafe_allow_html=True)

def render_extracted_fields(extracted, notes):
    area = "Urban"
    if extracted.get("Property_Area_Rural"):     area = "Rural"
    elif extracted.get("Property_Area_Semiurban"): area = "Semiurban"

    items = [
        ("Gender",            "Female" if extracted.get("Gender_Female") else "Male",           notes.get("gender","")),
        ("Married",           "Yes" if extracted.get("Married") else "No",                       notes.get("married","")),
        ("Dependents",        str(int(extracted.get("Dependents",0))),                           notes.get("dependents","")),
        ("Education",         "Graduate" if extracted.get("Education") else "Not Graduate",      notes.get("education","")),
        ("Self Employed",     "Yes" if extracted.get("Self_Employed") else "No",                 notes.get("self_employed","")),
        ("Applicant Income",  f"PKR {extracted.get('ApplicantIncome',0):,.0f}",                  notes.get("applicant_income","")),
        ("Co-Applicant Inc.", f"PKR {extracted.get('CoapplicantIncome',0):,.0f}",               notes.get("coapplicant_income","")),
        ("Loan Amount",       f"PKR {extracted.get('LoanAmount',0)*1000:,.0f}",                  notes.get("loan_amount","")),
        ("Loan Term",         f"{int(extracted.get('Loan_Amount_Term',360))} months",            notes.get("loan_term","")),
        ("Credit History",    "✅ Good" if extracted.get("Credit_History") else "❌ Bad",        notes.get("credit_history","")),
        ("Property Area",     area,                                                               notes.get("property_area","")),
    ]
    rows = "".join(
        f'<div class="field-row"><span class="field-label">{lbl}</span>'
        f'<span class="field-value">{val}<span class="field-note">{nt}</span></span></div>'
        for lbl, val, nt in items
    )
    st.markdown(
        f'<div class="card"><div class="card-title">🔍 NLP Extracted Fields '
        f'<span class="nlp-badge">AUTO</span></div>{rows}</div>',
        unsafe_allow_html=True
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <span class="hero-badge">🤖 AI-Powered · IntelliLoan</span>
  <h1 class="hero-title">Intelli<span>Loan</span></h1>
  <p class="hero-subtitle">Instant loan approval decisions powered by Machine Learning &amp; NLP</p>
</div>""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Mode")
    mode = st.radio("Input Method", ["📋 Manual Form", "📄 Document Upload (NLP)", "💬 Chatbot"])
    st.markdown("---")
    st.markdown("**IntelliLoan Features**")
    st.markdown("- RandomForest ML model\n- NLP document parser\n- OCR via PyMuPDF\n- Chatbot interface\n- FastAPI backend")
    st.markdown("---")
    st.markdown('<div style="color:rgba(255,255,255,.35);font-size:.75rem">FYP · IUB Rahim Yar Khan<br>Faizan Muneer · F22RSEEN1M01012</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════
#  MODE 1 — MANUAL FORM
# ════════════════════════════════════════════════════
if "📋" in mode:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="card"><div class="card-title">👤 Personal Information</div>', unsafe_allow_html=True)
        gender        = st.selectbox("Gender", ["Male","Female"])
        married       = st.selectbox("Married", ["No","Yes"])
        dependents    = st.selectbox("Dependents", [0,1,2,3])
        education     = st.selectbox("Education", ["Graduate","Not Graduate"])
        self_emp      = st.selectbox("Self Employed", ["No","Yes"])
        prop_area     = st.selectbox("Property Area", ["Urban","Semiurban","Rural"])
        credit        = st.selectbox("Credit History", [1,0], format_func=lambda x:"Good (1)" if x==1 else "Bad (0)")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div class="card-title">💰 Financial Details</div>', unsafe_allow_html=True)
        app_inc  = st.number_input("Applicant Income (PKR/month)",    0, value=50000, step=1000)
        coapp    = st.number_input("Co-Applicant Income (PKR/month)", 0, value=0,     step=1000)
        loan_amt = st.number_input("Loan Amount (thousands PKR)",     1, value=150,   step=5)
        loan_trm = st.selectbox("Loan Term (months)", [360,300,240,180,120,84,60,36,12])
        st.markdown('<div class="tip">💡 Good credit history + stable income = higher approval chances.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔍 Predict Loan Approval"):
        payload = {
            "Married":1 if married=="Yes" else 0, "Dependents":dependents,
            "Education":1 if education=="Graduate" else 0, "Self_Employed":1 if self_emp=="Yes" else 0,
            "ApplicantIncome":float(app_inc), "CoapplicantIncome":float(coapp),
            "LoanAmount":float(loan_amt), "Loan_Amount_Term":float(loan_trm),
            "Credit_History":int(credit), "Gender_Female":1 if gender=="Female" else 0,
            "Property_Area_Rural":1 if prop_area=="Rural" else 0,
            "Property_Area_Semiurban":1 if prop_area=="Semiurban" else 0,
            "Property_Area_Urban":1 if prop_area=="Urban" else 0,
        }
        with st.spinner("Analyzing…"):
            res = call_predict(payload)
        if "error" in res:
            st.error(f"⚠️ {res['error']} — Run: `uvicorn main:app --reload`")
        else:
            st.markdown("### 📊 Decision")
            render_result(res)
            st.markdown('<div class="card"><div class="card-title">📈 Summary</div>', unsafe_allow_html=True)
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Income", f"PKR {app_inc:,}")
            m2.metric("Loan",   f"PKR {loan_amt*1000:,}")
            m3.metric("Term",   f"{loan_trm} mo")
            m4.metric("Credit","✅ Good" if credit==1 else "❌ Bad")
            st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════
#  MODE 2 — DOCUMENT UPLOAD (NLP/ADU)
# ════════════════════════════════════════════════════
elif "📄" in mode:
    st.markdown("""
    <div class="card">
      <div class="card-title">📄 Automatic Document Understanding <span class="nlp-badge">NLP + OCR</span></div>
      <p style="color:#555;margin:0 0 4px">Upload a loan application, salary slip, or bank statement PDF.</p>
      <p style="color:#555;margin:0">IntelliLoan will <strong>automatically extract key fields</strong> using NLP and make an instant prediction.</p>
    </div>""", unsafe_allow_html=True)

    with st.expander(" What fields are extracted automatically?"):
        st.markdown("""
**Personal:** Gender, Marital Status, Dependents, Education, Employment  
**Financial:** Applicant Income, Co-Applicant Income, Loan Amount, Loan Term  
**Other:** Credit History / CIBIL Score, Property Area  

**Tips for best results:**
- Use text-based PDF (not a scanned image)
- Include labels like `Income: PKR 50,000` or `Loan Amount: 150,000`
- Mention degree name (e.g. "Bachelor", "Graduate") for education detection
        """)

    uploaded = st.file_uploader("Upload Loan Document (PDF)", type=["pdf"])

    if uploaded:
        st.markdown(f'<div class="tip">📎 <strong>{uploaded.name}</strong> &nbsp;·&nbsp; {uploaded.size/1024:.1f} KB</div>', unsafe_allow_html=True)

        if st.button("🧠 Analyze Document & Predict"):
            with st.spinner("🔍 Running NLP extraction…"):
                res = call_predict_document(uploaded.read(), uploaded.name)

            if "error" in res:
                st.error(f"⚠️ {res['error']}")
            else:
                st.markdown("### 📊 Prediction Result")
                render_result(res)
                st.markdown("---")

                left, right = st.columns(2, gap="large")
                with left:
                    render_extracted_fields(res.get("extracted_fields",{}), res.get("extraction_notes",{}))
                with right:
                    st.markdown('<div class="card"><div class="card-title">📝 Raw Text Preview</div>', unsafe_allow_html=True)
                    st.text_area("First 500 chars extracted from PDF:", res.get("raw_text_preview",""), height=210)
                    st.markdown('</div>', unsafe_allow_html=True)

                # ── Correction form ──
                st.markdown("---")
                st.markdown('<div class="card"><div class="card-title">✏️ Review & Correct Extracted Fields</div>'
                            '<p style="color:#666;font-size:.88rem;margin-top:-8px">Correct any wrong field and re-run the prediction.</p>',
                            unsafe_allow_html=True)
                ef = res.get("extracted_fields", {})
                area_idx = 0
                if ef.get("Property_Area_Rural"):     area_idx = 2
                elif ef.get("Property_Area_Semiurban"): area_idx = 1

                fc1, fc2 = st.columns(2)
                with fc1:
                    rg  = st.selectbox("Gender",        ["Male","Female"],            index=ef.get("Gender_Female",0))
                    rm  = st.selectbox("Married",        ["No","Yes"],                index=ef.get("Married",0))
                    rd  = st.selectbox("Dependents",     [0,1,2,3],                   index=min(ef.get("Dependents",0),3))
                    re_ = st.selectbox("Education",      ["Not Graduate","Graduate"],  index=ef.get("Education",0))
                    rs  = st.selectbox("Self Employed",  ["No","Yes"],                index=ef.get("Self_Employed",0))
                    rc  = st.selectbox("Credit History", [1,0],                       index=0 if ef.get("Credit_History",1)==1 else 1,
                                       format_func=lambda x:"Good" if x==1 else "Bad")
                with fc2:
                    ra  = st.selectbox("Property Area",  ["Urban","Semiurban","Rural"], index=area_idx)
                    ri  = st.number_input("Applicant Income (PKR)",     value=int(ef.get("ApplicantIncome",45000)), step=1000)
                    rci = st.number_input("Co-Applicant Income (PKR)",  value=int(ef.get("CoapplicantIncome",0)),   step=1000)
                    rla = st.number_input("Loan Amount (thousands)",    value=int(ef.get("LoanAmount",150)),        step=5)
                    rlt = st.number_input("Loan Term (months)",         value=int(ef.get("Loan_Amount_Term",360)),  step=12)
                st.markdown('</div>', unsafe_allow_html=True)

                if st.button("🔄 Re-Predict with Corrected Fields"):
                    corrected = {
                        "Married":1 if rm=="Yes" else 0, "Dependents":rd,
                        "Education":1 if re_=="Graduate" else 0, "Self_Employed":1 if rs=="Yes" else 0,
                        "ApplicantIncome":float(ri), "CoapplicantIncome":float(rci),
                        "LoanAmount":float(rla), "Loan_Amount_Term":float(rlt),
                        "Credit_History":int(rc), "Gender_Female":1 if rg=="Female" else 0,
                        "Property_Area_Rural":1 if ra=="Rural" else 0,
                        "Property_Area_Semiurban":1 if ra=="Semiurban" else 0,
                        "Property_Area_Urban":1 if ra=="Urban" else 0,
                    }
                    with st.spinner("Re-running…"):
                        new_res = call_predict(corrected)
                    if "error" in new_res:
                        st.error(new_res["error"])
                    else:
                        st.markdown("### 📊 Updated Prediction")
                        render_result(new_res)
    else:
        st.markdown("""
        <div class="doc-drop">
          <div style="font-size:3.5rem">📄</div>
          <p style="color:var(--teal);font-weight:600;font-size:1.1rem;margin:8px 0 4px">Drop your PDF here</p>
          <p style="color:#888;font-size:.9rem">Loan application · Salary slip · Bank statement</p>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
#  MODE 3 — CHATBOT
# ════════════════════════════════════════════════════
else:
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    if "chat_step"    not in st.session_state: st.session_state.chat_step = 0
    if "chat_data"    not in st.session_state: st.session_state.chat_data = {}

    QUESTIONS = [
        ("gender",             "Hi! Welcome to IntelliLoan 👋\n\nFirst — what is your **gender**? (Male / Female)"),
        ("married",            "Are you **married**? (Yes / No)"),
        ("dependents",         "How many **dependents** do you have? (0 / 1 / 2 / 3)"),
        ("education",          "**Education level**? (Graduate / Not Graduate)"),
        ("self_employed",      "Are you **self-employed**? (Yes / No)"),
        ("applicant_income",   "**Monthly income** in PKR? (e.g. 50000)"),
        ("coapplicant_income", "**Co-applicant's income** in PKR? (0 if none)"),
        ("loan_amount",        "**Loan amount** needed in thousands PKR? (e.g. 150)"),
        ("loan_term",          "**Loan term** in months? (e.g. 360)"),
        ("credit_history",     "**Good credit history**? (Yes / No)"),
        ("property_area",      "**Property area**? (Urban / Semiurban / Rural)"),
    ]

    def bot_reply(m): st.session_state.chat_history.append(("bot", m))
    def user_reply(m): st.session_state.chat_history.append(("user", m))

    if st.session_state.chat_step == 0 and not st.session_state.chat_history:
        bot_reply(QUESTIONS[0][1])

    st.markdown('<div class="card"><div class="card-title">💬 Loan Chatbot</div>', unsafe_allow_html=True)
    html = '<div class="chat-wrap">'
    for role, msg in st.session_state.chat_history:
        cls = "chat-bubble-user" if role=="user" else "chat-bubble-bot"
        html += f'<div class="{cls}">{msg.replace(chr(10),"<br>")}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.chat_step < len(QUESTIONS):
        inp = st.text_input("Your reply:", key=f"ci_{st.session_state.chat_step}", placeholder="Type here…")
        if inp:
            field = QUESTIONS[st.session_state.chat_step][0]
            user_reply(inp)
            st.session_state.chat_data[field] = inp.strip()
            st.session_state.chat_step += 1
            if st.session_state.chat_step < len(QUESTIONS):
                bot_reply(QUESTIONS[st.session_state.chat_step][1])
            else:
                bot_reply("✅ Analyzing your application…")
            st.rerun()

    elif st.session_state.chat_step == len(QUESTIONS):
        d = st.session_state.chat_data
        payload = {
            "Married":1 if d.get("married","").lower() in ["yes","y"] else 0,
            "Dependents":int(d.get("dependents","0")) if d.get("dependents","0").isdigit() else 0,
            "Education":1 if "grad" in d.get("education","").lower() else 0,
            "Self_Employed":1 if d.get("self_employed","").lower() in ["yes","y"] else 0,
            "ApplicantIncome":float(d.get("applicant_income","0").replace(",","") or 0),
            "CoapplicantIncome":float(d.get("coapplicant_income","0").replace(",","") or 0),
            "LoanAmount":float(d.get("loan_amount","150").replace(",","") or 150),
            "Loan_Amount_Term":float(d.get("loan_term","360").replace(",","") or 360),
            "Credit_History":1 if d.get("credit_history","").lower() in ["yes","y","1","good"] else 0,
            "Gender_Female":1 if "female" in d.get("gender","").lower() else 0,
            "Property_Area_Rural":1 if "rural" in d.get("property_area","").lower() else 0,
            "Property_Area_Semiurban":1 if "semi" in d.get("property_area","").lower() else 0,
            "Property_Area_Urban":1 if "urban" in d.get("property_area","").lower() and "semi" not in d.get("property_area","").lower() else 0,
        }
        res = call_predict(payload)
        if "error" in res:
            st.error(f"API Error: {res['error']} — Make sure FastAPI is running.")
        else:
            render_result(res)
        if st.button("🔄 New Application"):
            st.session_state.chat_history = []
            st.session_state.chat_step = 0
            st.session_state.chat_data = {}
            bot_reply(QUESTIONS[0][1])
            st.rerun()
