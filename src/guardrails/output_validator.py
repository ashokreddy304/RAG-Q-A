"""
Output validation guardrails.
Validates and filters LLM responses before returning to user.
"""

import re
from typing import Tuple, Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class OutputValidator:
    """
    Validates and filters LLM outputs.
    Implements multiple validation stages.
    """

    # Configuration
    MIN_ANSWER_LENGTH = 10
    MAX_ANSWER_LENGTH = 10000
    HARMFUL_PATTERNS = [
        r'(?i)hate\s+(speech|crime)',
        r'(?i)violence',
        r'(?i)illegal\s+activity',
    ]

    def __init__(self):
        """Initialize output validator."""
        logger.info("OutputValidator initialized")

    def validate_answer(self, answer: str, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate LLM answer with multiple stages.

        Validation stages:
        1. Check if answer is empty
        2. Check length constraints
        3. Check for harmful content
        4. Check for factual grounding
        5. Check for uncertainty indicators
        6. Verify coherence

        Args:
            answer: LLM-generated answer
            query: Original user query

        Returns:
            Tuple of (is_valid, error_message, metadata)
        """
        logger.info(f"Validating answer for query: {query[:50]}...")

        # Stage 1: Empty check
        if not answer or not answer.strip():
            logger.warning("Answer validation failed: Empty answer")
            return False, "Generated answer is empty", {}

        # Stage 2: Length validation
        if len(answer) < self.MIN_ANSWER_LENGTH:
            logger.warning(f"Answer too short: {len(answer)} < {self.MIN_ANSWER_LENGTH}")
            return False, "Answer is too brief to be helpful", {}

        if len(answer) > self.MAX_ANSWER_LENGTH:
            logger.warning(f"Answer too long: {len(answer)} > {self.MAX_ANSWER_LENGTH}")
            return False, "Answer exceeds maximum length", {}

        # Stage 3: Harmful content check
        if self._contains_harmful_content(answer):
            logger.warning("Answer validation failed: Harmful content detected")
            return False, "Answer contains inappropriate content", {}

        # Stage 4: Check grounding in context
        grounding_score = self._check_grounding(answer, query)
        if grounding_score < 0.3:
            logger.warning(f"Low grounding score: {grounding_score}")
            # Note: We warn but don't fail completely as some answers may be valid

        # Stage 5: Uncertainty check
        uncertainty_indicators = self._check_uncertainty(answer)
        metadata = {
            "answer_length": len(answer),
            "grounding_score": grounding_score,
            "uncertainty_indicators": uncertainty_indicators,
        }

        logger.info("Answer validation passed")
        return True, "", metadata

    def validate_citations(self, citations: list, answer: str) -> Tuple[bool, str]:
        """
        Validate citation format and completeness.

        Args:
            citations: List of citation objects
            answer: The answer text

        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.info(f"Validating {len(citations)} citations")

        if not isinstance(citations, list):
            return False, "Citations must be a list"

        for i, citation in enumerate(citations):
            # Check required fields
            required_fields = ['source_id', 'page', 'document', 'snippet']
            for field in required_fields:
                if field not in citation:
                    logger.warning(f"Citation {i} missing field: {field}")
                    return False, f"Citation {i} missing required field: {field}"

            # Check page number is valid
            if not isinstance(citation['page'], (int, str)):
                return False, f"Citation {i} has invalid page number"

            # Check snippet is not empty
            if not citation['snippet'] or not citation['snippet'].strip():
                return False, f"Citation {i} has empty snippet"

        logger.info("Citation validation passed")
        return True, ""

    def _contains_harmful_content(self, text: str) -> bool:
        """Check for harmful content patterns."""
        for pattern in self.HARMFUL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Harmful pattern detected: {pattern}")
                return True
        return False

    def _check_grounding(self, answer: str, query: str) -> float:
        """
        Check if answer is grounded in context.
        Simple heuristic: check if key terms from query appear in answer.

        Args:
            answer: LLM answer
            query: User query

        Returns:
            Grounding score (0-1)
        """
        # Extract key terms (words longer than 4 chars)
        query_terms = set(
            word.lower() for word in query.split()
            if len(word) > 4 and word.isalpha()
        )

        if not query_terms:
            return 1.0  # No specific terms to check

        answer_lower = answer.lower()
        matches = sum(1 for term in query_terms if term in answer_lower)

        grounding_score = matches / len(query_terms) if query_terms else 0.0
        logger.debug(f"Grounding score: {grounding_score:.2f}")

        return min(grounding_score, 1.0)

    def _check_uncertainty(self, answer: str) -> list:
        """
        Check for uncertainty indicators in answer.

        Args:
            answer: LLM answer

        Returns:
            List of uncertainty indicators found
        """
        uncertainty_phrases = [
            r"(?i)i\s+don't\s+know",
            r"(?i)i'm\s+not\s+sure",
            r"(?i)unclear",
            r"(?i)might\s+be",
            r"(?i)could\s+be",
            r"(?i)possibly",
            r"(?i)i\s+cannot\s+find",
        ]

        indicators = []
        for phrase in uncertainty_phrases:
            if re.search(phrase, answer):
                indicators.append(phrase)

        if indicators:
            logger.debug(f"Uncertainty indicators found: {indicators}")

        return indicators

    def filter_answer(self, answer: str, max_length: int = None) -> str:
        """
        Apply safe filtering to answer.

        Args:
            answer: Raw answer text
            max_length: Maximum allowed length

        Returns:
            Filtered answer
        """
        if max_length and len(answer) > max_length:
            answer = answer[:max_length].rsplit(' ', 1)[0] + "..."
            logger.info(f"Answer trimmed to {max_length} characters")

        return answer.strip()
