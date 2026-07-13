import os

from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_groq import ChatGroq


# =====================================================
# LOAD ENV
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

env_path = os.path.join(BASE_DIR, "Email", ".env")

load_dotenv(env_path)


# =====================================================
# LLM
# =====================================================

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.1
)


# =====================================================
# EMBEDDINGS
# =====================================================

_embeddings = None


def get_embeddings():

    global _embeddings

    if _embeddings is None:

        print("Loading HuggingFace Embeddings...")

        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    return _embeddings


# =====================================================
# LOAD ALL TXT FILES RECURSIVELY
# =====================================================

def load_all_documents(documents_folder):

    all_chunks = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    for root, dirs, files in os.walk(documents_folder):

        for file in files:

            if file.endswith(".txt"):

                file_path = os.path.join(
                    root,
                    file
                )

                loader = TextLoader(
                    file_path,
                    encoding="utf-8"
                )

                docs = loader.load()

                chunks = splitter.split_documents(
                    docs
                )

                all_chunks.extend(chunks)

    return all_chunks


# =====================================================
# CREATE VECTOR STORE
# =====================================================

def create_vectorstore(documents_folder):

    chunks = load_all_documents(
        documents_folder
    )

    vectorstore = FAISS.from_documents(
        chunks,
        get_embeddings()
    )

    return vectorstore


# =====================================================
# SAVE VECTOR STORE
# =====================================================

def save_vectorstore(
    vectorstore,
    save_path
):

    vectorstore.save_local(
        save_path
    )


# =====================================================
# LOAD VECTOR STORE
# =====================================================

def load_vectorstore(save_path):

    vectorstore = FAISS.load_local(
        save_path,
        get_embeddings(),
        allow_dangerous_deserialization=True
    )

    return vectorstore


# =====================================================
# ASK QUESTION
# =====================================================

def ask_question(
    question,
    vectorstore
):

    docs = vectorstore.similarity_search(
        question,
        k=4
    )

    context = "\n\n".join(
        [
            doc.page_content
            for doc in docs
        ]
    )

    prompt = f"""
You are the HIRIN AI Assistant.

Answer using ONLY the provided context.

If the context partially answers the question,
provide the best answer possible.

If no relevant information exists,
say:

I could not find that information.

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(
        prompt
    )

    return response.content