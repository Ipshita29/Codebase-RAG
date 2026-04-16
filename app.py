import streamlit as st
from rag import setup_rag
import os
import zipfile

st.set_page_config(page_title="Codebase RAG", layout="wide")

st.markdown("""
<h1 style='
    text-align: center;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #0f172a, #00c896);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
'>
    Codebase RAG 
</h1>

<p style='
    text-align: center;
    color: #64748b;
    margin-top: -10px;
'>
    Understand any codebase instantly
</p>
""", unsafe_allow_html=True)

# takes the input 

repo_url = st.text_input("GitHub Repo URL")

st.write("— OR —")

uploaded_files = st.file_uploader("Upload files / ZIP", accept_multiple_files=True)

load_clicked = st.button("Load Codebase")

# loading repi from github and upload files
if load_clicked:

    if not repo_url and not uploaded_files:
        st.error("Provide GitHub URL or upload files")

    else:
        with st.spinner("Processing..."):

            if repo_url:
                retriever, llm, repo_name, allowed, ignored = setup_rag(repo_url)

            else:
            
                if os.path.exists("uploaded_repo"):
                    import shutil
                    shutil.rmtree("uploaded_repo")

                os.makedirs("uploaded_repo", exist_ok=True)

                for f in uploaded_files:
                    if f.name.endswith(".zip"):
                        with zipfile.ZipFile(f, 'r') as zip_ref:
                            zip_ref.extractall("uploaded_repo")
                    else:
                        with open(os.path.join("uploaded_repo", f.name), "wb") as file:
                            file.write(f.getbuffer())

           
                retriever, llm, repo_name, allowed, ignored = setup_rag(
                    "uploaded_repo", is_local=True
                )

        
            st.session_state.retriever = retriever
            st.session_state.llm = llm
            st.session_state.repo_name = repo_name
            st.session_state.allowed = allowed
            st.session_state.ignored = ignored

            st.success("✅ Codebase Ready!")

# show info about the repo and files
if "repo_name" in st.session_state:

    st.subheader("Repository Info")

    st.write(f"Repo: {st.session_state.repo_name}")
    st.write(f"Allowed Files: {len(st.session_state.allowed)}")
    st.write(f"Ignored Files: {len(st.session_state.ignored)}")


if "retriever" in st.session_state:

    query = st.text_input("Ask something about the codebase")

    if query:
        with st.spinner("Thinking..."):

            docs = st.session_state.retriever.invoke(query)

            context = ""
            for d in docs:
                context += f"\nFile: {d.metadata.get('file_name')}\n{d.page_content[:300]}\n"

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

        st.subheader("Answer")
        st.write(response.content)