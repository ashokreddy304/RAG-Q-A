"""
Text chunking module for semantic text splitting.
Implements a recursive chunking strategy that respects paragraph boundaries.
"""

from typing import List, Dict, Any
import re
from config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TextChunker:
    """
    Chunking strategy using semantic boundaries.
    Recursively splits text at paragraph, sentence, and word level to maintain context.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize the text chunker.

        Args:
            chunk_size: Target size of each chunk (default from config)
            chunk_overlap: Overlap between chunks (default from config)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        logger.info(f"TextChunker initialized: size={self.chunk_size}, overlap={self.chunk_overlap}")

    def chunk_text(
        self,
        text: str,
        page_number: int = 1,
        source: str = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk text using recursive strategy.

        Chunking strategy (in order):
        1. Split by double newlines (paragraph breaks)
        2. Split by single newlines (lines)
        3. Split by sentence boundaries
        4. Split by words (if necessary)

        Args:
            text: Text to chunk
            page_number: Page number for metadata
            source: Source document name

        Returns:
            List of chunk dictionaries with text, page, and source metadata
        """
        if not text or len(text) == 0:
            logger.warning(f"Empty text provided for chunking on page {page_number}")
            return []

        # Clean text
        text = self._clean_text(text)

        # Split recursively
        chunks = self._recursive_split(text)

        # Create chunk objects with metadata
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            chunk_obj = {
                "text": chunk,
                "page_number": page_number,
                "source": source or "unknown",
                "chunk_index": i,
                "chunk_length": len(chunk),
            }
            chunk_objects.append(chunk_obj)

        logger.info(f"Chunked text into {len(chunk_objects)} chunks (page {page_number})")
        return chunk_objects

    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace while preserving paragraph structure."""
        # Remove multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        # Normalize line endings
        text = text.replace('\r\n', '\n')
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def _recursive_split(self, text: str) -> List[str]:
        """
        Recursively split text at semantic boundaries.

        Args:
            text: Text to split

        Returns:
            List of chunks
        """
        # Try splitting by double newlines (paragraphs)
        separators = ["\n\n", "\n", "(?<=[.!?]) ", " "]
        chunks = self._split_text(text, separators)

        # Merge small chunks and split large chunks
        merged_chunks = self._merge_and_split_chunks(chunks)

        return merged_chunks

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """
        Split text by the given separators in order.

        Args:
            text: Text to split
            separators: List of separators to try

        Returns:
            List of split text chunks
        """
        good_splits = []

        for separator in separators:
            if separator:
                # Try to use regex if separator looks like regex
                try:
                    if separator.startswith("(?"):
                        splits = re.split(separator, text)
                    else:
                        splits = text.split(separator)
                except Exception:
                    splits = text.split(separator)

                good_splits = [s for s in splits if s]
                if len(good_splits) > 1:
                    break

        return good_splits if good_splits else [text]

    def _merge_and_split_chunks(self, chunks: List[str]) -> List[str]:
        """
        Merge small chunks and split large chunks to respect chunk_size.

        Args:
            chunks: Initial chunks

        Returns:
            Merged and split chunks
        """
        separator = " "
        good_chunks = []
        current_chunk = ""

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            # If chunk is too large, split it further
            if len(chunk) > self.chunk_size:
                if current_chunk:
                    good_chunks.append(current_chunk)
                    current_chunk = ""

                # Split large chunk by spaces
                words = chunk.split()
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk) + len(word) > self.chunk_size:
                        if temp_chunk:
                            good_chunks.append(temp_chunk.strip())
                        temp_chunk = word
                    else:
                        temp_chunk += separator + word if temp_chunk else word

                if temp_chunk:
                    good_chunks.append(temp_chunk.strip())

            # Try to add to current chunk
            elif len(current_chunk) + len(chunk) < self.chunk_size:
                current_chunk += separator + chunk if current_chunk else chunk
            else:
                # Current chunk is full, start a new one
                if current_chunk:
                    good_chunks.append(current_chunk)
                current_chunk = chunk

        # Add remaining chunk
        if current_chunk:
            good_chunks.append(current_chunk)

        # Add overlap between chunks
        overlapped_chunks = self._add_overlap(good_chunks)

        return overlapped_chunks

    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """
        Add overlap between consecutive chunks for context preservation.

        Args:
            chunks: List of chunks without overlap

        Returns:
            Chunks with overlap
        """
        if len(chunks) <= 1:
            return chunks

        overlapped = [chunks[0]]

        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i]

            # Extract last words from previous chunk for overlap
            prev_words = prev_chunk.split()
            overlap_words = prev_words[-self.chunk_overlap:] if len(prev_words) > 0 else []

            # Create overlapped chunk
            if overlap_words:
                overlap_text = " ".join(overlap_words) + " " + current_chunk
                overlapped.append(overlap_text)
            else:
                overlapped.append(current_chunk)

        return overlapped
