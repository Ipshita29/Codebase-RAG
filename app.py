import streamlit as st
from rag import setup_rag

st.set_page_config(page_title="Codebase RAG", layout="wide")

st.title("💻 Codebase RAG Assistant")

repo_url = st.text_input("Enter GitHub Repo URL:")

# LOAD CODEBASE
if st.button("Load Codebase"):

    if not repo_url:
        st.error("Please enter a valid GitHub URL")
    else:
        with st.spinner("Cloning & processing repo..."):
            try:
                retriever, llm, repo_name, allowed, ignored = setup_rag(repo_url)

                st.session_state.retriever = retriever
                st.session_state.llm = llm

                st.success("✅ Codebase Loaded Successfully!")

                st.write(f"📁 Repo: {repo_name}")
                st.write(f"📊 Allowed Files: {len(allowed)}")
                st.write(f"🚫 Ignored Files: {len(ignored)}")

                with st.expander("📂 Allowed Files"):
                    for f in allowed[:50]:
                        st.write(f)

                with st.expander("🚫 Ignored Files"):
                    for f in ignored[:50]:
                        st.write(f)

            except Exception as e:
                st.error(str(e))


# QUERY SECTION
query = st.text_input("Ask your question:")

if query and "retriever" in st.session_state:

    with st.spinner("Thinking..."):

        docs = st.session_state.retriever.invoke(query)

        context = ""
        for doc in docs:
            context += f"\nFile: {doc.metadata.get('file_name')}\n{doc.page_content[:300]}\n"

        prompt = f"""
            You are an expert code assistant.

            Answer STRICTLY in this format:

            1. Paragraph explanation
            2. Bullet points
            3. File names where code exists

            Do NOT copy raw code unnecessarily.

            Context:
            {context[:2000]}

            Question: {query}

            Answer:
            """

        response = st.session_state.llm.invoke(prompt)

    st.write("### 🤖 Answer:")
    st.write(response.content)

    st.write("### 📂 Sources:")
    for doc in docs:
        st.write(f"📄 {doc.metadata.get('file_name')}")
        st.code(doc.page_content[:200])