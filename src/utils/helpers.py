"""
Helper functions for the RAG application.
Includes utilities for document processing, text manipulation, etc.
"""

import re
from typing import List, Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def extract_page_numbers(text: str, original_text: str) -> List[int]:
    """
    Extract page numbers from metadata (placeholder implementation).
    In production, this would track page breaks during PDF parsing.

    Args:
        text: Chunk text
        original_text: Full document text

    Returns:
        List of page numbers
    """
    # This is a simplified version. In production, page numbers would be
    # tracked during PDF parsing using pdfplumber's page metadata
    try:
        pos = original_text.find(text)
        if pos != -1:
            page_num = original_text[:pos].count('\n') // 30 + 1
            return [page_num]
    except Exception as e:
        logger.warning(f"Could not extract page number: {e}")
    return [1]  # Default to page 1


def format_citation(page_num: int, snippet: str, source: str = None) -> str:
    """
    Format a citation with page number and snippet.

    Args:
        page_num: Page number
        snippet: Text snippet to cite
        source: Optional source document name

    Returns:
        Formatted citation string
    """
    citation = f"[Page {page_num}]"
    if source:
        citation += f" ({source})"
    if snippet:
        snippet = snippet[:100] + "..." if len(snippet) > 100 else snippet
        citation += f': "{snippet}"'
    return citation


def batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    Split a list into batches.

    Args:
        items: List to batch
        batch_size: Size of each batch

    Returns:
        List of batches
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
