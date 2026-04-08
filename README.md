# Codebase RAG Assistant

Understand any GitHub repository instantly using AI 🚀

---

## Overview

**Codebase RAG Assistant** is a Retrieval-Augmented Generation (RAG) based web app that allows users to explore and understand any codebase by simply asking questions.

Instead of manually reading hundreds of files, users can:

* Ask natural language questions
* Get context-aware answers
* See relevant source files instantly

---

## How It Works

This project follows a simple RAG pipeline:

1. **Input**

   * User provides a GitHub repository URL or uploads files

2. **Data Processing**

   * Repository is cloned locally
   * Only relevant files are selected (`.py`, `.js`, `.md`, etc.)
   * Files are split into smaller chunks

3. **Vectorization**

   * Chunks are converted into embeddings using `all-MiniLM-L6-v2`
   * Stored in a FAISS vector database

4. **Query Handling**

   * User asks a question
   * Query is enhanced for better retrieval

5. **Retrieval**

   * Top relevant chunks are fetched from FAISS

6. **Generation**

   * LLM (LLaMA 3 via Groq) generates answer using retrieved context

---

## Features

* Ask questions about any codebase
* Automatic GitHub repo ingestion
* Context-aware AI answers
* Source file highlighting
* Fast responses using Groq API
* Clean and modern UI (Streamlit)

---

## Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **RAG Framework:** LangChain
* **Vector DB:** FAISS
* **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`)
* **LLM:** LLaMA 3 (via Groq API)
* **Version Control:** GitPython

---

## Project Structure

```
Codebase-RAG/
│
├── app.py          # Streamlit frontend
├── rag.py          # RAG pipeline logic
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone <your-repo-url>
cd Codebase-RAG
pip install -r requirements.txt
```

---

## Setup Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

## Run the App

```bash
streamlit run app.py
```

---

## Example Queries

* "What is this project about?"
* "How does authentication work?"
* "Which files handle API calls?"
* "Explain the main functionality"

---

## Limitations

* Works best with meaningful file content (README, structured code)
* May struggle with very vague queries
* Relies on retrieved context (no external knowledge)

---

## Future Improvements

* Better semantic query understanding
* Chat history memory
* Repo summary button
* File tree visualization
* Deployment support

---

## Acknowledgements

* LangChain
* Hugging Face
* Groq
* Streamlit

---

