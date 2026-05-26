"""
Retrieval module for semantic search and document retrieval.
Handles embedding generation and similarity-based retrieval.
"""

from typing import List, Dict, Any, Tuple
from langchain_openai import OpenAIEmbeddings
from config import settings
from src.vector_store.faiss_store import FAISSVectorStore
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Retriever:
    """
    Retriever for semantic search using embeddings.
    Handles embedding generation and similarity search.
    """

    def __init__(self, vector_store: FAISSVectorStore = None):
        """
        Initialize the retriever.

        Args:
            vector_store: FAISS vector store instance
        """
        self.vector_store = vector_store or FAISSVectorStore()

        # Initialize embedding model
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )

        logger.info("Retriever initialized successfully")

    def add_documents(
        self,
        chunks: List[Dict[str, Any]]
    ) -> None:
        """
        Add document chunks to the vector store.

        Args:
            chunks: List of chunk dictionaries with 'text' and metadata
        """
        if not chunks:
            logger.warning("No chunks to add")
            return

        try:
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")

            # Extract texts
            texts = [chunk['text'] for chunk in chunks]

            # Generate embeddings
            embeddings = self.embeddings.embed_documents(texts)

            # Add to vector store
            self.vector_store.add_embeddings(embeddings, chunks)

            logger.info(f"Successfully added {len(chunks)} chunks to vector store")

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def retrieve(
        self,
        query: str,
        k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.

        Retrieval Strategy:
        - Generates embedding for the query
        - Performs similarity search using L2 distance
        - Returns top-k most similar chunks with metadata
        - Filters by similarity threshold

        Args:
            query: Query text
            k: Number of results to return (default from config)

        Returns:
            List of relevant chunks with metadata and similarity scores
        """
        k = k or settings.top_k_results

        try:
            logger.info(f"Retrieving top {k} documents for query: {query[:100]}")

            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)

            # Search vector store
            results, distances = self.vector_store.search(query_embedding, k)

            # Convert L2 distances to similarity scores (lower distance = higher similarity)
            # L2 distance range: 0 (identical) to ~2 (opposite in normalized space)
            scored_results = []
            for result, distance in zip(results, distances):
                # Convert distance to similarity (0-1 scale)
                # Using formula: similarity = 1 / (1 + distance)
                similarity = 1 / (1 + distance)

                # Apply threshold filter
                if similarity >= settings.similarity_threshold:
                    result_with_score = {**result, "similarity_score": similarity}
                    scored_results.append(result_with_score)

            logger.info(f"Retrieved {len(scored_results)} relevant documents")
            return scored_results

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise

    def clear(self) -> None:
        """Clear all documents from the vector store."""
        try:
            self.vector_store.clear()
            logger.info("Cleared all documents from retriever")
        except Exception as e:
            logger.error(f"Error clearing retriever: {str(e)}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        return {
            "embedding_model": settings.embedding_model,
            "embedding_dimension": settings.embedding_dimension,
            "vector_store_stats": self.vector_store.get_stats(),
        }
