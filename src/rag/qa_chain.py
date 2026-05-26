"""
QA Chain for generating answers with citations.
Implements RAG with prompt engineering and citation extraction.
"""

from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from src.rag.retriever import Retriever
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class QAChain:
    """
    QA Chain using LLM with RAG context and citations.
    Generates grounded answers with proper source attribution.
    """

    def __init__(self, retriever: Retriever = None):
        """
        Initialize the QA chain.

        Args:
            retriever: Retriever instance for document retrieval
        """
        self.retriever = retriever or Retriever()

        # Initialize LLM
        logger.info(f"Loading LLM: {settings.openai_model}")
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            temperature=0.7,
            openai_api_key=settings.openai_api_key,
        )

        logger.info("QA Chain initialized successfully")

    def generate_answer(
        self,
        query: str,
        chat_history: List[Dict[str, str]] = None,
        k: int = None
    ) -> Dict[str, Any]:
        """
        Generate an answer with citations for the given query.

        Args:
            query: User query
            chat_history: List of previous messages for context
            k: Number of documents to retrieve

        Returns:
            Dictionary with answer, sources, and citations
        """
        chat_history = chat_history or []

        try:
            logger.info(f"Generating answer for query: {query[:100]}")

            # Retrieve relevant documents
            retrieved_docs = self.retriever.retrieve(query, k)

            if not retrieved_docs:
                logger.warning("No relevant documents found")
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "citations": [],
                }

            # Build context from retrieved documents
            context = self._build_context(retrieved_docs)

            # Generate answer using LLM
            answer = self._generate_llm_response(query, context, chat_history)

            # Extract citations
            citations = self._extract_citations(retrieved_docs)

            result = {
                "answer": answer,
                "sources": retrieved_docs,
                "citations": citations,
            }

            logger.info(f"Generated answer with {len(citations)} citations")
            return result

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved documents.

        Args:
            documents: List of relevant documents

        Returns:
            Formatted context string
        """
        context = "RETRIEVED CONTEXT:\n"

        for i, doc in enumerate(documents, 1):
            page_num = doc.get('page_number', 'N/A')
            source = doc.get('source', 'Unknown')
            text = doc.get('text', '')[:500]  # Limit text length

            context += f"\n[Document {i} - Page {page_num} from {source}]\n"
            context += f"{text}\n"

        return context

    def _generate_llm_response(
        self,
        query: str,
        context: str,
        chat_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate response from LLM with context and history.

        Args:
            query: User query
            context: Retrieved context
            chat_history: Previous messages

        Returns:
            Generated answer text
        """
        # Build system prompt
        system_prompt = SystemMessage(content="""You are a helpful AI assistant that answers questions based on provided documents.

Your responsibility:
1. Answer questions using ONLY the information provided in the retrieved context
2. Be clear about what information comes from the documents
3. If you cannot answer based on the context, say so explicitly
4. Reference the source documents in your answer (e.g., "According to Document 1...")
5. Keep answers concise and factual

Important: Do NOT make up information that is not in the provided context.""")

        # Build messages
        messages = [system_prompt]

        # Add chat history
        for msg in chat_history[-6:]:  # Keep last 3 exchanges
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append({"role": "assistant", "content": msg['content']})

        # Add context and current query
        user_message = f"""{context}

Based on the above context, please answer the following question:

Question: {query}

Answer (reference the document and page numbers where relevant):"""

        messages.append(HumanMessage(content=user_message))

        # Generate response
        response = self.llm.invoke(messages)
        return response.content

    def _extract_citations(self, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract and format citations from retrieved documents.

        Args:
            documents: List of retrieved documents

        Returns:
            List of citation dictionaries
        """
        citations = []

        for i, doc in enumerate(documents, 1):
            page_num = doc.get('page_number', 'N/A')
            source = doc.get('source', 'Unknown')
            text = doc.get('text', '')

            # Extract first 150 characters as snippet
            snippet = (text[:150] + "...") if len(text) > 150 else text

            citation = {
                "source_id": i,
                "page": page_num,
                "document": source,
                "snippet": snippet,
                "similarity_score": doc.get('similarity_score', 0.0),
            }

            citations.append(citation)

        return citations

    def clear_context(self) -> None:
        """Clear all documents from the retriever."""
        try:
            self.retriever.clear()
            logger.info("Cleared context from QA chain")
        except Exception as e:
            logger.error(f"Error clearing context: {str(e)}")
            raise
