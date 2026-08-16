from pydantic import BaseModel

from app.rag.retriever import retrieve_policies


class PolicyResult(BaseModel):
    content: str
    source: str


def search_policy(query: str, k: int = 3) -> list[PolicyResult]:
    """
    Search company policies for information relevant to the query.
    """

    documents = retrieve_policies(query=query, k=k)

    return [
        PolicyResult(
            content=document.page_content,
            source=document.metadata["source"],
        )
        for document in documents
    ]