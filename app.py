import streamlit as st
from utils.file_handler import fetch_github_files, extract_zip_files
from utils.filter import filter_files, format_report

st.set_page_config(
    page_title="Codebase RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;700;800&display=swap');
:root {
    --bg:      #ffffff;
    --surface: #f8fafc;
    --border:  #e2e8f0;
    --accent:  #00c896;
    --text:    #0f172a;
    --muted:   #64748b;
    --warn:    #f59e0b;
}
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 900px; }
.hero { text-align: center; padding: 3rem 0 2rem; }
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
.hero-sub { font-size: 1rem; color: var(--muted); margin-top: 0.8rem; }
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
}
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.4rem;
}
.stTextInput input, .stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
}
.stFileUploader > div {
    background: #ffffff !important;
    border: 1px dashed var(--border) !important;
}
.stButton button {
    width: 100%;
    background: var(--accent) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: bold;
}
.output-box {
    background: #ffffff;
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 10px;
    padding: 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.7;
    white-space: pre-wrap;
}
.stat-box {
    text-align: center;
    padding: 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
}
.stat-num {
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
}
.stat-label { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }

.file-item {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    padding: 5px 12px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    margin: 3px 0;
    color: var(--muted);
    display: flex;
    justify-content: space-between;
}
.file-item .priority-tag {
    color: var(--accent);
    font-size: 0.65rem;
    border: 1px solid rgba(0,200,150,0.3);
    border-radius: 10px;
    padding: 1px 7px;
}
.report-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.8;
    color: #166534;
    white-space: pre-wrap;
}
.skipped-note {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--warn);
    margin-top: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for key, default in {
    "answer": None,
    "files": [],
    "filter_report": None,
    "source_label": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">🧠 RAG · TF-IDF · Logistic Regression</div>
    <h1 class="hero-title">Codebase RAG</h1>
    <p class="hero-sub">Ask questions about any GitHub repo or ZIP</p>
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
github_url = st.text_input("GitHub URL", placeholder="https://github.com/user/repo")
st.markdown("<div style='text-align:center;color:#64748b;font-size:0.85rem;margin:8px 0'>— or —</div>", unsafe_allow_html=True)
zip_file = st.file_uploader("Upload ZIP", type=["zip"])

# ── Load Button ───────────────────────────────────────────────────────────────
if st.button("📂  Load Codebase"):
    if not github_url and not zip_file:
        st.warning("Please provide a GitHub URL or upload a ZIP file.")
    elif github_url and zip_file:
        st.warning("Please use only one input — GitHub URL or ZIP, not both.")
    else:
        with st.spinner("Fetching files..."):
            if github_url:
                raw_files, error = fetch_github_files(github_url)
                label = f"GitHub: {github_url.strip().rstrip('/')}"
            else:
                raw_files, error = extract_zip_files(zip_file.read())
                label = f"ZIP: {zip_file.name}"

        if error:
            st.error(f"❌ {error}")
        else:
            # ── Phase 3: Run smart filter ──
            with st.spinner("Filtering files..."):
                filtered, report = filter_files(raw_files)

            st.session_state.files        = filtered
            st.session_state.filter_report = report
            st.session_state.source_label = label
            st.session_state.answer       = None

            skipped = report["total_input"] - report["passed"]
            st.success(f"✅ Loaded {report['passed']} files after filtering  ({skipped} skipped)")

# ── Stats + Filter Report ─────────────────────────────────────────────────────
if st.session_state.files:
    files  = st.session_state.files
    report = st.session_state.filter_report

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Codebase Summary</p>', unsafe_allow_html=True)

    total_lines = sum(len(f["content"].splitlines()) for f in files)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{report["passed"]}</div><div class="stat-label">Files</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{total_lines:,}</div><div class="stat-label">Lines</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{report["priority_files"]}</div><div class="stat-label">Priority</div></div>', unsafe_allow_html=True)
    with c4:
        skipped = report["total_input"] - report["passed"]
        st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#f59e0b">{skipped}</div><div class="stat-label">Skipped</div></div>', unsafe_allow_html=True)

    # Filter report detail
    with st.expander("🔍 Filter Report"):
        st.markdown(f'<div class="report-box">{format_report(report)}</div>', unsafe_allow_html=True)

    # File list
    with st.expander(f"📁 {report['passed']} files passed filtering"):
        for f in files:
            priority_tag = '<span class="priority-tag">⭐ priority</span>' if f.get("is_priority") else ""
            lines = len(f["content"].splitlines())
            st.markdown(
                f'<div class="file-item"><span>📄 {f["path"]} &nbsp;·&nbsp; {f["size_kb"]}KB &nbsp;·&nbsp; {lines} lines</span>{priority_tag}</div>',
                unsafe_allow_html=True
            )

# ── Question ──────────────────────────────────────────────────────────────────
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
question = st.text_area("Ask a question", placeholder="e.g. How does authentication work in this project?")

if st.button("🔍  Analyze & Answer"):
    if not st.session_state.files:
        st.warning("Please load a codebase first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        st.session_state.answer = (
            f"[Placeholder — LLM answer coming in Phase 8]\n\n"
            f"Source   : {st.session_state.source_label}\n"
            f"Files    : {len(st.session_state.files)}\n"
            f"Question : {question}"
        )

if st.session_state.answer:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Answer</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="output-box">{st.session_state.answer}</div>', unsafe_allow_html=True)