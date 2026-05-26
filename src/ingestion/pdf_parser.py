"""
PDF parsing and text extraction module.
Uses pdfplumber for robust text extraction with metadata tracking.
"""

import pdfplumber
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFParser:
    """
    Robust PDF parser using pdfplumber.
    Extracts text while preserving page metadata for citation purposes.
    """

    def __init__(self, pdf_path: str):
        """
        Initialize the PDF parser.

        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.pdf_name = Path(pdf_path).name
        self.pages_data: List[Dict[str, Any]] = []

        logger.info(f"Initializing PDFParser for: {self.pdf_name}")

    def extract_text(self) -> List[Dict[str, Any]]:
        """
        Extract text from PDF with page metadata.

        Returns:
            List of dictionaries with page number, text, and metadata
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"PDF contains {total_pages} pages")

                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text
                    text = page.extract_text()
                    if not text:
                        logger.warning(f"No text extracted from page {page_num}")
                        text = "[Page contains only images or is blank]"

                    # Extract tables if any
                    tables = page.extract_tables()
                    table_text = ""
                    if tables:
                        for table_idx, table in enumerate(tables):
                            table_text += f"\n[TABLE {table_idx + 1}]\n"
                            # Simple table formatting
                            for row in table:
                                table_text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                        logger.info(f"Extracted {len(tables)} table(s) from page {page_num}")

                    # Combine text and table data
                    full_text = text + table_text

                    # Create page data object
                    page_data = {
                        "page_number": page_num,
                        "text": full_text,
                        "source": self.pdf_name,
                        "page_height": page.height,
                        "page_width": page.width,
                    }

                    self.pages_data.append(page_data)

                logger.info(f"Successfully extracted text from {len(self.pages_data)} pages")

            return self.pages_data

        except FileNotFoundError:
            logger.error(f"PDF file not found: {self.pdf_path}")
            raise
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def get_full_text(self) -> str:
        """
        Get concatenated text from all pages.

        Returns:
            Full document text
        """
        if not self.pages_data:
            self.extract_text()

        full_text = ""
        for page in self.pages_data:
            full_text += f"\n--- Page {page['page_number']} ---\n"
            full_text += page['text']

        return full_text

    def get_metadata(self) -> Dict[str, Any]:
        """
        Extract PDF metadata.

        Returns:
            PDF metadata dictionary
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                metadata = pdf.metadata
                return {
                    "title": metadata.get("Title", self.pdf_name),
                    "author": metadata.get("Author", "Unknown"),
                    "pages": len(pdf.pages),
                    "creation_date": metadata.get("CreationDate", "Unknown"),
                }
        except Exception as e:
            logger.warning(f"Could not extract metadata: {str(e)}")
            return {"title": self.pdf_name, "pages": len(self.pages_data)}
