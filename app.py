import streamlit as st

st.set_page_config(
    page_title="Codebase RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Root Variables ── */
:root {
    --bg:        #ffffff;
    --surface:   #f8fafc;
    --border:    #e2e8f0;
    --accent:    #00c896;
    --accent2:   #3d6aff;
    --text:      #0f172a;
    --muted:     #64748b;
    --danger:    #ef4444;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 900px; }

/* ── Hero Section ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    color: var(--accent);
    background: rgba(0,200,150,0.08);
    border: 1px solid rgba(0,200,150,0.25);
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 1.2rem;
    text-transform: uppercase;
}
.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #0f172a 30%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1rem;
    color: var(--muted);
    margin-top: 0.8rem;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
}

/* Labels */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
}

/* OR separator */
.or-sep {
    text-align: center;
    margin: 1rem 0;
    color: var(--muted);
}

/* Inputs */
.stTextInput input,
.stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
}

/* File uploader */
.stFileUploader > div {
    background: #ffffff !important;
    border: 1px dashed var(--border) !important;
}

/* Button */
.stButton button {
    width: 100%;
    background: var(--accent) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: bold;
}

/* Output */
.output-box {
    background: #ffffff;
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 10px;
    padding: 1.5rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Pipeline */
.pipeline {
    text-align: center;
    margin-bottom: 1rem;
}
.pipe-step {
    display: inline-block;
    padding: 4px 10px;
    border: 1px solid var(--border);
    border-radius: 20px;
    margin: 2px;
    font-size: 0.7rem;
    color: var(--muted);
}
.pipe-step.active {
    color: var(--accent);
    border-color: var(--accent);
}
</style>
""", unsafe_allow_html=True)

if "answer" not in st.session_state:
    st.session_state.answer = None

st.markdown("""
<div class="hero">
    <div class="hero-badge">🧠 RAG · TF-IDF · Logistic Regression</div>
    <h1 class="hero-title">Codebase RAG</h1>
    <p class="hero-sub">Ask questions about any GitHub repo or ZIP</p>
</div>
""", unsafe_allow_html=True)

github_url = st.text_input("GitHub URL")
zip_file = st.file_uploader("Upload ZIP", type=["zip"])

question = st.text_area("Ask a question")

if st.button("Analyze"):
    st.session_state.answer = "Processing..."

if st.session_state.answer:
    st.markdown(f'<div class="output-box">{st.session_state.answer}</div>', unsafe_allow_html=True)

