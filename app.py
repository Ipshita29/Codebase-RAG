import streamlit as st
from rag import setup_rag
import os

st.set_page_config(page_title="Codebase RAG", layout="wide")

# -------------------------------
# 🎨 CSS
# -------------------------------
st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap');

            :root {
                --bg:#ffffff;
                --surface:#f8fafc;
                --border:#e2e8f0;
                --accent:#00c896;
                --text:#0f172a;
                --muted:#64748b;
            }

            html, body, [class*="css"] {
                font-family: 'Syne', sans-serif;
                background: var(--bg);
                color: var(--text);
            }

            #MainMenu, footer, header {visibility:hidden;}

            .block-container {
                max-width: 800px;
                padding-top: 2rem;
            }

            /* HERO */
            .hero {
                text-align:center;
                padding: 2rem 0 1rem;
            }

            .hero-title {
                font-size: 2.8rem;
                font-weight: 800;
                background: linear-gradient(135deg,#0f172a 40%, #00c896 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .hero-sub {
                color: var(--muted);
                margin-top: 0.4rem;
            }

            /* CARD */
            .card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 1.5rem;
                margin-bottom: 1rem;
            }

            /* LABEL */
            .section-label {
                font-size: 0.7rem;
                letter-spacing: 0.15em;
                text-transform: uppercase;
                color: var(--muted);
                margin-bottom: 0.6rem;
            }

            /* INPUT */
            .stTextInput input {
                border-radius: 10px !important;
                border: 1px solid var(--border) !important;
                font-family: 'JetBrains Mono', monospace !important;
            }
            /* BUTTON */
            .stButton button {
                width: 100%;
                border-radius: 10px;
                background: var(--accent);
                color: white;
                font-weight: 600;
            }

            /* OUTPUT */
            .output-box {
                background: white;
                border-left: 4px solid var(--accent);
                border-radius: 10px;
                padding: 1rem;
                font-family: 'JetBrains Mono', monospace;
            }

            /* OR */
            .or-sep {
                text-align: center;
                margin: 1rem 0;
                color: var(--muted);
                font-size: 0.75rem;
                letter-spacing: 0.2em;
            }

            /* PIPELINE */
            .pipeline {
                text-align: center;
                margin: 1rem 0;
            }
            .pipe-step {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                border: 1px solid var(--border);
                margin: 4px;
                font-size: 0.7rem;
            }
            .pipe-step.active {
                border-color: var(--accent);
                color: var(--accent);
            }
            </style>
            """, unsafe_allow_html=True)


# -------------------------------
# HERO
# -------------------------------
st.markdown("""
<div class="hero">
    <h1 class="hero-title">Codebase RAG</h1>
    <p class="hero-sub">Understand any codebase instantly</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# INPUT
# -------------------------------

st.markdown('<div class="section-label">Repository</div>', unsafe_allow_html=True)

repo_url = st.text_input("GitHub URL")

st.markdown('<div class="or-sep">— OR —</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)

load_clicked = st.button("Load Codebase")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# LOAD
# -------------------------------
if load_clicked:

    if not repo_url and not uploaded_files:
        st.error("Provide GitHub URL or upload files")

    else:
        with st.spinner("Processing..."):

            if repo_url:
                retriever, llm, repo_name, allowed, ignored = setup_rag(repo_url)
            else:
                os.makedirs("uploaded_repo", exist_ok=True)

                for f in uploaded_files:
                    with open(os.path.join("uploaded_repo", f.name), "wb") as file:
                        file.write(f.getbuffer())

                retriever, llm, repo_name, allowed, ignored = setup_rag("uploaded_repo")

            # ✅ STORE EVERYTHING
            st.session_state.retriever = retriever
            st.session_state.llm = llm
            st.session_state.repo_name = repo_name
            st.session_state.allowed = allowed
            st.session_state.ignored = ignored

            st.success("Codebase Ready!")

# -------------------------------
# 📊 SHOW REPO INFO
# -------------------------------
if "repo_name" in st.session_state:
    st.markdown('<div class="section-label">Repository Info</div>', unsafe_allow_html=True)

    st.write(f"Repo: {st.session_state.repo_name}")
    st.write(f"Total Files: {len(st.session_state.allowed) + len(st.session_state.ignored)}")
    st.write(f"Allowed Files: {len(st.session_state.allowed)}")
    st.write(f"Ignored Files: {len(st.session_state.ignored)}")

    with st.expander("📂 Allowed Files"):
        for f in st.session_state.allowed[:50]:
            st.write(f)

    with st.expander("🚫 Ignored Files"):
        for f in st.session_state.ignored[:50]:
            st.write(f)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# QUERY
# -------------------------------
if "retriever" in st.session_state:

    st.markdown('<div class="section-label">Ask</div>', unsafe_allow_html=True)

    query = st.text_input("Ask about the codebase")

    st.markdown('</div>', unsafe_allow_html=True)

    if query:

        with st.spinner("Thinking..."):

            docs_scores = st.session_state.retriever.vectorstore.similarity_search_with_score(query, k=4)
            docs = [d for d, s in docs_scores if s < 0.8]

            context = ""
            for d in docs:
                context += f"\nFile: {d.metadata.get('file_name')}\n{d.page_content[:200]}\n"

                prompt = f"""
                            You are an expert code assistant.

                            Strict rules:
                            - Answer ONLY using the given context
                            - DO NOT guess or hallucinate
                            - If answer is not present → say "No relevant information found"

                            Format:
                            1. Clear paragraph explanation
                            2. Bullet points (if useful)
                            3. Mention exact file names

                            Context:
                            {context}

                            Question:
                            {query}

                            Answer:
                            """

            response = st.session_state.llm.invoke(prompt)

        # ANSWER
        st.markdown('<div class="section-label">Answer</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="output-box">{response.content}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # SOURCES
        st.markdown('<div class="section-label">Sources</div>', unsafe_allow_html=True)

        shown = set()

        for d in docs:
            file_name = d.metadata.get("file_name")
            content = d.page_content.lower()

            if file_name not in shown and any(word in content for word in query.lower().split()):
                shown.add(file_name)
                st.write(f"📄 {file_name}")
                st.code(d.page_content[:150])

        if not shown:
            st.write("No strongly relevant files found.")

        st.markdown('</div>', unsafe_allow_html=True)