import streamlit as st
from utils.file_handler import fetch_github_files, extract_zip_files
from utils.filter import filter_files, format_report
from utils.chunker import chunk_all_files
from ml.vectorizer import build_vectorizer

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
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--accent) !important; }
.stFileUploader > div { background: #ffffff !important; border: 1px dashed var(--border) !important; }
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
.stat-num { font-size: 2rem; font-weight: 800; color: var(--accent); font-family: 'JetBrains Mono', monospace; }
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
}
.chunk-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 6px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
}
.chunk-header { color: var(--accent); font-size: 0.68rem; margin-bottom: 4px; font-weight: 600; }
.chunk-body { color: var(--text); white-space: pre-wrap; line-height: 1.5; max-height: 120px; overflow: hidden; }
.cap-warning {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #92400e;
    margin-top: 0.5rem;
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
.tfidf-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.8;
    color: #1e40af;
}
.term-pill {
    display: inline-block;
    background: rgba(0,200,150,0.1);
    border: 1px solid rgba(0,200,150,0.3);
    color: #065f46;
    border-radius: 20px;
    padding: 2px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    margin: 2px 3px;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for key, default in {
    "answer": None,
    "files": [],
    "chunks": [],
    "vectorizer": None,
    "tfidf_matrix": None,
    "filter_report": None,
    "chunk_report": None,
    "vec_report": None,
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
            with st.spinner("Filtering files..."):
                filtered, filter_report = filter_files(raw_files)

            with st.spinner("Chunking code..."):
                chunks, chunk_report = chunk_all_files(filtered)

            with st.spinner("Building TF-IDF vectors..."):
                vectorizer, tfidf_matrix, vec_report = build_vectorizer(chunks)

            st.session_state.files         = filtered
            st.session_state.chunks        = chunks
            st.session_state.vectorizer    = vectorizer
            st.session_state.tfidf_matrix  = tfidf_matrix
            st.session_state.filter_report = filter_report
            st.session_state.chunk_report  = chunk_report
            st.session_state.vec_report    = vec_report
            st.session_state.source_label  = label
            st.session_state.answer        = None

            st.success(
                f"✅ {filter_report['passed']} files → "
                f"{chunk_report['total_chunks']} chunks → "
                f"{vec_report['n_features']} TF-IDF features"
            )

# ── Stats ─────────────────────────────────────────────────────────────────────
if st.session_state.files and st.session_state.filter_report and st.session_state.chunk_report:
    files         = st.session_state.files
    chunks        = st.session_state.chunks
    filter_report = st.session_state.filter_report
    chunk_report  = st.session_state.chunk_report
    vec_report    = st.session_state.vec_report

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Pipeline Stats</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{filter_report["passed"]}</div><div class="stat-label">Files</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{chunk_report["total_chunks"]}</div><div class="stat-label">Chunks</div></div>', unsafe_allow_html=True)
    with c3:
        n_feat = vec_report["n_features"] if vec_report else 0
        st.markdown(f'<div class="stat-box"><div class="stat-num">{n_feat}</div><div class="stat-label">TF-IDF Features</div></div>', unsafe_allow_html=True)
    with c4:
        vocab = vec_report["vocab_size"] if vec_report else 0
        st.markdown(f'<div class="stat-box"><div class="stat-num">{vocab}</div><div class="stat-label">Vocab Size</div></div>', unsafe_allow_html=True)

    if chunk_report["capped"]:
        st.markdown('<div class="cap-warning">⚠️ Chunk cap reached (200). Some chunks were trimmed.</div>', unsafe_allow_html=True)

    # TF-IDF info
    if vec_report and "top_terms" in vec_report:
        with st.expander("📊 TF-IDF Vectorizer Info"):
            pills = "".join(f'<span class="term-pill">{t}</span>' for t in vec_report["top_terms"])
            st.markdown(f"""
            <div class="tfidf-box">
                <b>Chunks vectorized :</b> {vec_report['n_chunks']}<br>
                <b>Feature dimensions:</b> {vec_report['n_features']}<br>
                <b>Vocabulary size   :</b> {vec_report['vocab_size']}<br>
                <b>Top informative terms:</b><br>
                <div style="margin-top:6px">{pills}</div>
            </div>
            """, unsafe_allow_html=True)

    # Filter report
    with st.expander("🔍 Filter Report"):
        st.markdown(f'<div class="report-box">{format_report(filter_report)}</div>', unsafe_allow_html=True)

    # Chunk preview
    with st.expander(f"🧩 Preview chunks ({chunk_report['total_chunks']} total)"):
        show_n = min(10, len(chunks))
        st.caption(f"Showing first {show_n} of {len(chunks)} chunks")
        for chunk in chunks[:show_n]:
            preview = chunk["content"][:300] + ("..." if len(chunk["content"]) > 300 else "")
            st.markdown(f"""
            <div class="chunk-card">
                <div class="chunk-header">📄 {chunk['file_path']}  ·  chunk #{chunk['chunk_index']}  ·  {chunk['line_count']} lines</div>
                <div class="chunk-body">{preview}</div>
            </div>
            """, unsafe_allow_html=True)

    # File list
    with st.expander(f"📁 {filter_report['passed']} files loaded"):
        for f in files:
            lines = len(f["content"].splitlines())
            st.markdown(f'<div class="file-item">📄 {f["path"]} &nbsp;·&nbsp; {f["size_kb"]}KB &nbsp;·&nbsp; {lines} lines</div>', unsafe_allow_html=True)

# ── Question ──────────────────────────────────────────────────────────────────
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
question = st.text_area("Ask a question", placeholder="e.g. How does authentication work in this project?")

if st.button("🔍  Analyze & Answer"):
    if not st.session_state.chunks:
        st.warning("Please load a codebase first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        st.session_state.answer = (
            f"[Placeholder — LLM answer coming in Phase 8]\n\n"
            f"Source  : {st.session_state.source_label}\n"
            f"Files   : {len(st.session_state.files)}\n"
            f"Chunks  : {len(st.session_state.chunks)}\n"
            f"Features: {st.session_state.vec_report['n_features']}\n"
            f"Question: {question}"
        )

if st.session_state.answer:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Answer</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="output-box">{st.session_state.answer}</div>', unsafe_allow_html=True)