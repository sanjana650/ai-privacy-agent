from pathlib import Path

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parents[2]
POLICY_DIR = BASE_DIR / "data"

POLICY_FILES = [
    "pii_policy.txt",
    "logging_policy.txt",
    "retention_policy.txt",
    "incident_policy.txt",
]


def load_policy_documents() -> list[Document]:
    documents: list[Document] = []

    for filename in POLICY_FILES:
        file_path = POLICY_DIR / filename

        text = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=text,
                metadata={"source": filename},
            )
        )

    return documents


def split_documents(
    documents: list[Document],
) -> list[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    return splitter.split_documents(documents)


def build_vector_store() -> Chroma:
    documents = load_policy_documents()
    chunks = split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="privacy_policies",
    )


# Build ONCE when module loads
vector_store = build_vector_store()


def retrieve_policies(
    query: str,
    k: int = 3,
) -> list[Document]:

    return vector_store.similarity_search(
        query=query,
        k=k,
    )