"""
FAISS-based vector store for semantic search.
Provides persistent storage and efficient similarity search capabilities.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import faiss

from config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class FAISSVectorStore:
    """
    FAISS-based vector store with local persistence.
    Stores embeddings and their metadata for efficient semantic search.
    """

    def __init__(self, embedding_dim: int = None, store_path: str = None):
        """
        Initialize the FAISS vector store.

        Args:
            embedding_dim: Dimension of embeddings (default from config)
            store_path: Path to store index (default from config)
        """
        self.embedding_dim = embedding_dim or settings.embedding_dimension
        self.store_path = store_path or settings.vector_store_path

        # Create storage directory
        Path(self.store_path).parent.mkdir(parents=True, exist_ok=True)

        self.index_path = os.path.join(self.store_path, "index.faiss")
        self.metadata_path = os.path.join(self.store_path, "metadata.pkl")

        # Initialize FAISS index
        self.index: faiss.IndexFlatL2 = None
        self.metadata: List[Dict[str, Any]] = []

        logger.info(f"Initializing FAISSVectorStore at {self.store_path}")
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create a new one."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}. Creating new one.")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata = []
        logger.info("Created new FAISS index")

    def add_embeddings(
        self,
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ) -> None:
        """
        Add embeddings to the vector store.

        Args:
            embeddings: List of embedding vectors
            metadata: List of metadata dictionaries corresponding to embeddings
        """
        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata lists must have the same length")

        if len(embeddings) == 0:
            logger.warning("No embeddings to add")
            return

        try:
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)

            # Normalize embeddings for better results
            faiss.normalize_L2(embeddings_array)

            # Add to index
            self.index.add(embeddings_array)

            # Store metadata
            self.metadata.extend(metadata)

            logger.info(f"Added {len(embeddings)} embeddings to vector store")

            # Persist to disk
            self._save_index()

        except Exception as e:
            logger.error(f"Error adding embeddings: {str(e)}")
            raise

    def search(
        self,
        query_embedding: List[float],
        k: int = None
    ) -> Tuple[List[Dict[str, Any]], List[float]]:
        """
        Search for similar vectors in the store.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return (default from config)

        Returns:
            Tuple of (metadata list, distances list)
        """
        k = k or settings.top_k_results

        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return [], []

        try:
            # Convert and normalize query
            query_array = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_array)

            # Search
            distances, indices = self.index.search(query_array, min(k, self.index.ntotal))

            # Extract results
            results = []
            result_distances = []

            for idx, distance in zip(indices[0], distances[0]):
                if idx >= 0:  # Valid index
                    results.append(self.metadata[idx])
                    result_distances.append(float(distance))

            logger.info(f"Found {len(results)} similar vectors for query")
            return results, result_distances

        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise

    def clear(self) -> None:
        """Clear all embeddings and metadata from the store."""
        try:
            self._create_new_index()
            self._save_index()
            logger.info("Cleared vector store")
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            raise

    def _save_index(self) -> None:
        """Persist index and metadata to disk."""
        try:
            # Create directory if needed
            Path(self.store_path).mkdir(parents=True, exist_ok=True)

            # Save index
            faiss.write_index(self.index, self.index_path)

            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)

            logger.debug("Saved FAISS index and metadata to disk")

        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_vectors": self.index.ntotal,
            "embedding_dimension": self.embedding_dim,
            "store_path": self.store_path,
            "metadata_count": len(self.metadata),
        }
