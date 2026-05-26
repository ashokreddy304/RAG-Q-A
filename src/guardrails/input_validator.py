"""
Input validation guardrails.
Validates user inputs before processing.
"""

import re
from typing import Tuple, Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class InputValidator:
    """
    Validates and sanitizes user inputs.
    Implements multiple validation stages.
    """

    # Configuration
    MAX_QUERY_LENGTH = 5000
    MIN_QUERY_LENGTH = 3
    MAX_FILE_SIZE_MB = 100
    BLOCKED_PATTERNS = [
        r'(?i)malware',
        r'(?i)exploit',
        r'(?i)hacking',
    ]

    def __init__(self):
        """Initialize input validator."""
        logger.info("InputValidator initialized")

    def validate_query(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate user query with multiple stages.

        Validation stages:
        1. Check if query is empty
        2. Check length constraints
        3. Check for SQL injection patterns
        4. Check for prompt injection
        5. Sanitize special characters
        6. Check for blocked patterns

        Args:
            query: User query string

        Returns:
            Tuple of (is_valid, error_message, metadata)
        """
        logger.info(f"Validating query: {query[:50]}...")

        # Stage 1: Empty check
        if not query or not query.strip():
            logger.warning("Query validation failed: Empty query")
            return False, "Query cannot be empty", {}

        # Stage 2: Length validation
        if len(query) < self.MIN_QUERY_LENGTH:
            logger.warning(f"Query validation failed: Too short ({len(query)} < {self.MIN_QUERY_LENGTH})")
            return False, f"Query must be at least {self.MIN_QUERY_LENGTH} characters", {}

        if len(query) > self.MAX_QUERY_LENGTH:
            logger.warning(f"Query validation failed: Too long ({len(query)} > {self.MAX_QUERY_LENGTH})")
            return False, f"Query cannot exceed {self.MAX_QUERY_LENGTH} characters", {}

        # Stage 3: SQL injection check
        if self._contains_sql_injection(query):
            logger.warning("Query validation failed: Potential SQL injection detected")
            return False, "Query contains potentially malicious patterns", {}

        # Stage 4: Prompt injection check
        if self._contains_prompt_injection(query):
            logger.warning("Query validation failed: Potential prompt injection detected")
            return False, "Query contains prompt manipulation attempts", {}

        # Stage 5: Blocked patterns check
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, query):
                logger.warning(f"Query validation failed: Blocked pattern matched - {pattern}")
                return False, "Query contains restricted content", {}

        # Stage 6: Sanitize and clean
        sanitized_query = self._sanitize_query(query)

        logger.info("Query validation passed")
        return True, "", {"original_length": len(query), "sanitized": sanitized_query}

    def validate_pdf_file(self, file_path: str, file_size_mb: float) -> Tuple[bool, str]:
        """
        Validate PDF file before processing.

        Args:
            file_path: Path to PDF file
            file_size_mb: File size in MB

        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.info(f"Validating PDF file: {file_path}")

        # Check file extension
        if not file_path.lower().endswith('.pdf'):
            logger.warning(f"File validation failed: Not a PDF - {file_path}")
            return False, "File must be a PDF document"

        # Check file size
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            logger.warning(f"File validation failed: Too large ({file_size_mb}MB > {self.MAX_FILE_SIZE_MB}MB)")
            return False, f"File size cannot exceed {self.MAX_FILE_SIZE_MB}MB"

        logger.info("PDF file validation passed")
        return True, ""

    def validate_chat_history(self, chat_history: list) -> Tuple[bool, str]:
        """
        Validate chat history structure.

        Args:
            chat_history: List of chat messages

        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.info("Validating chat history")

        if not isinstance(chat_history, list):
            return False, "Chat history must be a list"

        for i, msg in enumerate(chat_history):
            if not isinstance(msg, dict):
                return False, f"Message {i} is not a dictionary"

            if 'role' not in msg or 'content' not in msg:
                return False, f"Message {i} missing required fields"

            if msg['role'] not in ['user', 'assistant']:
                return False, f"Message {i} has invalid role"

            if not isinstance(msg['content'], str):
                return False, f"Message {i} content is not a string"

        logger.info("Chat history validation passed")
        return True, ""

    def _contains_sql_injection(self, text: str) -> bool:
        """Check for SQL injection patterns."""
        sql_patterns = [
            r"('\s*(OR|AND)\s*'|'\s*=\s*')",
            r"(DROP|DELETE|INSERT|UPDATE|SELECT)\s+",
            r"(;|--|\*)",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _contains_prompt_injection(self, text: str) -> bool:
        """Check for prompt injection patterns."""
        injection_patterns = [
            r"(?i)ignore\s+previous",
            r"(?i)system\s+prompt",
            r"(?i)forget\s+instructions",
            r"(?i)override",
            r"(?i)jailbreak",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, text):
                return True
        return False

    def _sanitize_query(self, query: str) -> str:
        """Sanitize and clean query string."""
        # Remove excessive whitespace
        query = re.sub(r'\s+', ' ', query).strip()

        # Remove null bytes
        query = query.replace('\0', '')

        # Remove control characters
        query = ''.join(char for char in query if ord(char) >= 32 or char in '\n\t')

        return query
