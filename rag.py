import os
import shutil
import git
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

load_dotenv()

IGNORE_FOLDERS = ["node_modules", ".git", "venv", "__pycache__", "build", "dist"]
ALLOWED_EXTENSIONS = (".py", ".js", ".ts", ".jsx", ".tsx", ".md")


def load_github_repo(repo_url):
    repo_path = "temp_repo"

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    git.Repo.clone_from(repo_url, repo_path)

    repo_name = repo_url.split("/")[-1]

    documents = []
    allowed_files = []
    ignored_files = []

    for root, dirs, files in os.walk(repo_path):

        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(ALLOWED_EXTENSIONS):
                try:
                    loader = TextLoader(file_path, encoding="utf-8")
                    docs = loader.load()

                    for doc in docs:
                        doc.metadata["file_name"] = file
                        doc.metadata["file_path"] = file_path

                    documents.extend(docs)
                    allowed_files.append(file_path)

                except:
                    ignored_files.append(file_path)
            else:
                ignored_files.append(file_path)

    return documents[:80], repo_name, allowed_files, ignored_files


def setup_rag(repo_url):

    documents, repo_name, allowed_files, ignored_files = load_github_repo(repo_url)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = FAISS.from_documents(chunks, embeddings)

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    llm = ChatGroq(
        model="llama-3.1-8b-instant",   
        api_key=os.getenv("GROQ_API_KEY")
    )

    return retriever, llm, repo_name, allowed_files, ignored_files