import streamlit as st
from rag import setup_rag

st.title("💻 Codebase RAG Assistant")

repo_url = st.text_input("Enter GitHub Repo URL:")

# LOAD
if st.button("Load Codebase"):

    if not repo_url:
        st.error("Please enter a valid URL")
    else:
        with st.spinner("Cloning & processing repo..."):

            try:
                retriever, llm, repo_name, allowed, ignored = setup_rag(repo_url)

                st.session_state.retriever = retriever
                st.session_state.llm = llm

                st.success("✅ Codebase Loaded!")

                st.write(f"📁 Repo: {repo_name}")
                st.write(f"✅ Allowed Files: {len(allowed)}")
                st.write(f"❌ Ignored Files: {len(ignored)}")

                # Dropdowns
                with st.expander("📂 Allowed Files"):
                    for f in allowed[:50]:
                        st.write(f)

                with st.expander("🚫 Ignored Files"):
                    for f in ignored[:50]:
                        st.write(f)

            except Exception as e:
                st.error(str(e))


# QUERY
query = st.text_input("Ask your question:")

if query and "retriever" in st.session_state:

    with st.spinner("Thinking..."):

        docs = st.session_state.retriever.invoke(query)

        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""
        Based on the context below, answer briefly.

        {context[:1500]}

        Question: {query}
        Answer:
        """

        response = st.session_state.llm.invoke(prompt)

    st.write("### 🤖 Answer:")
    st.write(response)

    st.write("### 📂 Sources:")
    for doc in docs:
        st.write(f"📄 {doc.metadata.get('file_name')}")
        st.code(doc.page_content[:200])