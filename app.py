import streamlit as st
from rag import setup_rag

st.set_page_config(page_title="Codebase RAG", layout="wide")

st.title("💻 Codebase RAG Assistant")

# -------------------------------
# 🔥 LLM-based filtering function
# -------------------------------
def filter_docs_with_llm(docs, query, llm):
    filtered = []

    for doc in docs:
        check_prompt = f"""
            Is this document relevant to the question?

            Answer only YES or NO.

            Document:
            {doc.page_content[:300]}

            Question:
            {query}
            """
        try:
            res = llm.invoke(check_prompt).content.lower()
            if "yes" in res:
                filtered.append(doc)
        except:
            continue

    return filtered


# -------------------------------
# INPUT
# -------------------------------
repo_url = st.text_input("Enter GitHub Repo URL:")

# -------------------------------
# LOAD CODEBASE
# -------------------------------
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


# -------------------------------
# QUERY
# -------------------------------
query = st.text_input("Ask your question:")

if query and "retriever" in st.session_state:

    with st.spinner("Thinking..."):

        # 🔹 Step 1: similarity search with scores
        docs_with_scores = st.session_state.retriever.vectorstore.similarity_search_with_score(query, k=5)

        # 🔹 Step 2: score filtering (dynamic)
        docs = [doc for doc, score in docs_with_scores if score < 1.0]

        # # 🔹 Step 3: LLM-based filtering
        # docs = filter_docs_with_llm(docs, query, st.session_state.llm)

        # 🔹 Step 4: build clean context
        context = ""
        for doc in docs:
            context += f"\nFile: {doc.metadata.get('file_name')}\n{doc.page_content[:300]}\n"

        # 🔹 Step 5: strict prompt
        prompt = f"""
You are a strict code assistant.

Rules:
- Answer ONLY from context
- DO NOT guess
- If unsure → say "No issues found"

Format:
1. Paragraph
2. Bullet points (if needed)
3. File names

Context:
{context[:2000]}

Question: {query}

Answer:
"""

        response = st.session_state.llm.invoke(prompt)

    # -------------------------------
    # OUTPUT
    # -------------------------------
    st.write("### 🤖 Answer:")
    st.write(response.content)

    st.write("### 📂 Sources:")

    if "no issues found" in response.content.lower():
        st.write("No relevant files needed.")
    else:
        if docs:
            for doc in docs:
                st.write(f"📄 {doc.metadata.get('file_name')}")
                st.code(doc.page_content[:200])
        else:
            st.write("No relevant documents found.")