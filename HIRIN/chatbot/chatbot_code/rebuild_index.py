import os

from rag import (
    create_vectorstore,
    save_vectorstore
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

documents_path = os.path.join(
    BASE_DIR,
    "documents"
)

index_path = os.path.join(
    BASE_DIR,
    "faiss_index"
)


print("Loading Documents...")

vectorstore = create_vectorstore(
    documents_path
)

print("Creating FAISS Index...")

save_vectorstore(
    vectorstore,
    index_path
)

print("\nFAISS Index Created Successfully")